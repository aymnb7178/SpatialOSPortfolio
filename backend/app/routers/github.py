import json
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..config import get_settings
from ..database import get_db
from ..models import GithubRepository, GithubSyncState, User
from ..schemas import GithubRepositoryAdminUpdate

router = APIRouter(prefix="/github", tags=["github"])
admin_router = APIRouter(prefix="/admin/github", tags=["admin-github"])
_sync_lock = threading.Lock()
GITHUB_API = "https://api.github.com"


def _json(value: str, fallback: Any):
    try:
        return json.loads(value or "")
    except (TypeError, ValueError):
        return fallback


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _repo_payload(item: GithubRepository) -> dict:
    return {
        "id": item.id,
        "github_id": item.github_id,
        "name": item.name,
        "full_name": item.full_name,
        "description": item.description,
        "html_url": item.html_url,
        "homepage": item.homepage,
        "language": item.language,
        "languages": _json(item.languages_json, {}),
        "topics": _json(item.topics_json, []),
        "stars": item.stars,
        "forks": item.forks,
        "watchers": item.watchers,
        "open_issues": item.open_issues,
        "size_kb": item.size_kb,
        "default_branch": item.default_branch,
        "created_at": _iso(item.created_at_github),
        "updated_at": _iso(item.updated_at_github),
        "pushed_at": _iso(item.pushed_at_github),
        "archived": item.archived,
        "is_fork": item.is_fork,
        "is_featured": item.is_featured,
        "is_visible": item.is_visible,
        "sort_order": item.sort_order,
        "synced_at": _iso(item.synced_at),
    }


class GithubRemoteError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502, reset_at: datetime | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.reset_at = reset_at


class GithubClient:
    def __init__(self):
        settings = get_settings()
        self.username = settings.github_username.strip() or "aymnb7178"
        self.token = settings.github_token.strip()
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "SpatialOS-Portfolio-GitHub-Intelligence",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.remaining: int | None = None
        self.reset_at: datetime | None = None

    def get(self, path: str, params: dict | None = None) -> Any:
        try:
            with httpx.Client(timeout=12.0, follow_redirects=True, headers=self.headers) as client:
                response = client.get(f"{GITHUB_API}{path}", params=params)
        except httpx.HTTPError as exc:
            raise GithubRemoteError("تعذر الاتصال بـ GitHub") from exc
        self.remaining = _int_header(response, "x-ratelimit-remaining")
        reset = _int_header(response, "x-ratelimit-reset")
        self.reset_at = datetime.fromtimestamp(reset, tz=timezone.utc) if reset else None
        if response.status_code == 403 and self.remaining == 0:
            raise GithubRemoteError("تم الوصول إلى حد GitHub API، سيتم استخدام البيانات المخزنة مؤقتاً", 429, self.reset_at)
        if response.status_code == 404:
            raise GithubRemoteError("بيانات GitHub غير موجودة", 404)
        if response.status_code >= 400:
            raise GithubRemoteError("أعاد GitHub استجابة غير متوقعة", 502)
        return response.json()

    def profile(self) -> dict:
        return self.get(f"/users/{self.username}")

    def repos(self) -> list[dict]:
        return self.get(f"/users/{self.username}/repos", {"per_page": 100, "sort": "updated", "direction": "desc", "type": "owner"})

    def events(self) -> list[dict]:
        return self.get(f"/users/{self.username}/events/public", {"per_page": 20})

    def languages(self, full_name: str) -> dict:
        return self.get(f"/repos/{full_name}/languages")

    def readme(self, full_name: str) -> str:
        data = self.get(f"/repos/{full_name}/readme")
        if data.get("encoding") == "base64":
            import base64
            return base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
        return data.get("content", "") or ""


def _int_header(response: httpx.Response, name: str) -> int | None:
    try:
        value = response.headers.get(name)
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _event_payload(event: dict) -> dict:
    actor = event.get("actor") or {}
    repo = event.get("repo") or {}
    return {
        "id": event.get("id", ""),
        "type": event.get("type", "Event"),
        "repo": repo.get("name", ""),
        "actor": actor.get("display_login") or actor.get("login") or "",
        "created_at": event.get("created_at"),
        "public": bool(event.get("public", True)),
    }


def _profile_payload(profile: dict) -> dict:
    return {
        "login": profile.get("login", ""),
        "name": profile.get("name") or profile.get("login", ""),
        "avatar_url": profile.get("avatar_url", ""),
        "html_url": profile.get("html_url", ""),
        "bio": profile.get("bio") or "",
        "public_repos": profile.get("public_repos", 0),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "public_gists": profile.get("public_gists", 0),
        "created_at": profile.get("created_at"),
        "updated_at": profile.get("updated_at"),
    }


def _repo_from_remote(remote: dict, languages: dict, current: GithubRepository | None = None) -> GithubRepository:
    item = current or GithubRepository(github_id=int(remote["id"]), full_name=remote.get("full_name", ""), name=remote.get("name", ""), html_url=remote.get("html_url", ""))
    item.github_id = int(remote["id"])
    item.name = remote.get("name", "")[:160]
    item.full_name = remote.get("full_name", "")[:255]
    item.description = remote.get("description") or ""
    item.html_url = remote.get("html_url") or ""
    item.homepage = remote.get("homepage") or ""
    item.language = remote.get("language") or ""
    item.languages_json = json.dumps(languages or {}, ensure_ascii=False)
    item.topics_json = json.dumps(remote.get("topics") or [], ensure_ascii=False)
    item.stars = int(remote.get("stargazers_count") or 0)
    item.forks = int(remote.get("forks_count") or 0)
    item.watchers = int(remote.get("watchers_count") or 0)
    item.open_issues = int(remote.get("open_issues_count") or 0)
    item.size_kb = int(remote.get("size") or 0)
    item.default_branch = remote.get("default_branch") or "main"
    item.created_at_github = _dt(remote.get("created_at"))
    item.updated_at_github = _dt(remote.get("updated_at"))
    item.pushed_at_github = _dt(remote.get("pushed_at"))
    item.archived = bool(remote.get("archived"))
    item.is_fork = bool(remote.get("fork"))
    return item


def sync_github(db: Session) -> GithubSyncState:
    if not _sync_lock.acquire(blocking=False):
        state = db.scalar(select(GithubSyncState).where(GithubSyncState.username == get_settings().github_username))
        if state:
            return state
        raise GithubRemoteError("المزامنة قيد التنفيذ")
    try:
        client = GithubClient()
        state = db.scalar(select(GithubSyncState).where(GithubSyncState.username == client.username))
        if not state:
            state = GithubSyncState(id=1, username=client.username)
            db.add(state)
            db.flush()
        profile = client.profile()
        repos = client.repos()
        events = client.events()
        language_totals: dict[str, int] = {}
        seen: set[int] = set()
        for position, remote in enumerate(repos):
            if not remote.get("id"):
                continue
            seen.add(int(remote["id"]))
            current = db.scalar(select(GithubRepository).where(GithubRepository.github_id == int(remote["id"])))
            languages = client.languages(remote.get("full_name", "")) if remote.get("full_name") else {}
            item = _repo_from_remote(remote, languages, current)
            if current is None:
                item.sort_order = position
                db.add(item)
            for language, bytes_count in languages.items():
                language_totals[language] = language_totals.get(language, 0) + int(bytes_count or 0)
        state.profile_json = json.dumps(_profile_payload(profile), ensure_ascii=False)
        state.activity_json = json.dumps([_event_payload(item) for item in events], ensure_ascii=False)
        state.language_totals_json = json.dumps(language_totals, ensure_ascii=False)
        state.last_sync_at = datetime.now(timezone.utc)
        state.rate_limit_remaining = client.remaining
        state.rate_limit_reset_at = client.reset_at
        state.last_error = ""
        db.commit()
        db.refresh(state)
        return state
    except GithubRemoteError as exc:
        db.rollback()
        username = get_settings().github_username.strip() or "aymnb7178"
        state = db.scalar(select(GithubSyncState).where(GithubSyncState.username == username))
        if state:
            state.last_error = str(exc)
            db.commit()
        raise
    finally:
        _sync_lock.release()


def _fresh(state: GithubSyncState | None) -> bool:
    if not state or not state.last_sync_at:
        return False
    ttl = max(5, get_settings().github_cache_ttl_minutes)
    last = state.last_sync_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last < timedelta(minutes=ttl)


def _state_payload(state: GithubSyncState) -> dict:
    return {
        "profile": _json(state.profile_json, {}),
        "activity": _json(state.activity_json, []),
        "languages": _json(state.language_totals_json, {}),
        "last_sync_at": _iso(state.last_sync_at),
        "rate_limit_remaining": state.rate_limit_remaining,
        "rate_limit_reset_at": _iso(state.rate_limit_reset_at),
        "last_error": state.last_error,
    }


def _visible_repositories(db: Session) -> list[GithubRepository]:
    return db.scalars(
        select(GithubRepository)
        .where(GithubRepository.is_visible.is_(True), GithubRepository.archived.is_(False))
        .order_by(GithubRepository.is_featured.desc(), GithubRepository.sort_order, GithubRepository.stars.desc(), GithubRepository.id)
    ).all()


def _get_state(db: Session, allow_sync: bool = True) -> GithubSyncState:
    username = get_settings().github_username.strip() or "aymnb7178"
    state = db.scalar(select(GithubSyncState).where(GithubSyncState.username == username))
    if allow_sync and not _fresh(state):
        try:
            state = sync_github(db)
        except GithubRemoteError as exc:
            if state:
                return state
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    if not state:
        raise HTTPException(status_code=503, detail="بيانات GitHub غير متاحة بعد")
    return state


@router.get("/overview")
def github_overview(db: Session = Depends(get_db)):
    state = _get_state(db)
    repos = _visible_repositories(db)
    payload = _state_payload(state)
    payload["profile"] = {**payload["profile"], "stars": sum(item.stars for item in repos)}
    return {**payload, "repositories": [_repo_payload(item) for item in repos]}


@router.get("/repos")
def github_repositories(language: str | None = Query(default=None, max_length=80), sort: str = Query(default="updated", pattern="^(updated|stars|name)$"), q: str = Query(default="", max_length=120), db: Session = Depends(get_db)):
    _get_state(db)
    query = select(GithubRepository).where(GithubRepository.is_visible.is_(True), GithubRepository.archived.is_(False))
    if language:
        query = query.where(GithubRepository.language.ilike(language.strip()))
    if q.strip():
        term = f"%{q.strip()}%"
        query = query.where((GithubRepository.name.ilike(term)) | (GithubRepository.description.ilike(term)))
    if sort == "stars":
        query = query.order_by(GithubRepository.stars.desc(), GithubRepository.name)
    elif sort == "name":
        query = query.order_by(GithubRepository.name)
    else:
        query = query.order_by(GithubRepository.updated_at_github.desc(), GithubRepository.name)
    return [_repo_payload(item) for item in db.scalars(query).all()]


@router.get("/repos/{repo_name}")
def github_repository(repo_name: str, db: Session = Depends(get_db)):
    _get_state(db)
    item = db.scalar(select(GithubRepository).where(GithubRepository.name == repo_name, GithubRepository.is_visible.is_(True)))
    if not item:
        raise HTTPException(status_code=404, detail="المستودع غير موجود")
    if not item.readme_markdown:
        try:
            item.readme_markdown = GithubClient().readme(item.full_name)
            db.commit()
        except GithubRemoteError:
            pass
    return {**_repo_payload(item), "readme_markdown": item.readme_markdown}


@admin_router.get("/repos")
def admin_github_repositories(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [_repo_payload(item) for item in db.scalars(select(GithubRepository).order_by(GithubRepository.sort_order, GithubRepository.name)).all()]


@admin_router.patch("/repos/{repo_id}")
def admin_update_github_repository(repo_id: int, data: GithubRepositoryAdminUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(GithubRepository, repo_id)
    if not item:
        raise HTTPException(status_code=404, detail="المستودع غير موجود")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return _repo_payload(item)


@admin_router.post("/sync")
def admin_sync_github(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        state = sync_github(db)
    except GithubRemoteError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return _state_payload(state)
