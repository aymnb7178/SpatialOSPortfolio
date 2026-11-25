import json
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import Project, User
from ..schemas import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])
admin_router = APIRouter(prefix="/admin/projects", tags=["admin-projects"])


def _json(value, fallback=None):
    try:
        return json.loads(value or "[]")
    except (TypeError, ValueError):
        return fallback if fallback is not None else []


def _payload(item: Project) -> dict:
    data = {column.name: getattr(item, column.name) for column in Project.__table__.columns}
    data["features"] = _json(item.features_json)
    data["technologies"] = _json(item.technologies_json)
    data["media_urls"] = _json(item.media_json)
    data["related_slugs"] = _json(item.related_slugs_json)
    for key in ("features_json", "technologies_json", "media_json", "related_slugs_json"):
        data.pop(key, None)
    return data


def _apply(item: Project, data: dict) -> None:
    for field in ("slug", "title", "title_ar", "eyebrow", "category", "summary", "summary_ar", "overview", "overview_ar", "problem", "problem_ar", "solution", "solution_ar", "architecture", "architecture_ar", "challenges", "challenges_ar", "results", "results_ar", "hero_media_url", "github_url", "demo_url", "is_featured", "is_visible", "sort_order"):
        if field in data:
            value = data[field]
            setattr(item, field, value.strip() if isinstance(value, str) else value)
    if "features" in data:
        item.features_json = json.dumps(data["features"], ensure_ascii=False)
    if "technologies" in data:
        item.technologies_json = json.dumps(data["technologies"], ensure_ascii=False)
    if "media_urls" in data:
        item.media_json = json.dumps(data["media_urls"], ensure_ascii=False)
    if "related_slugs" in data:
        item.related_slugs_json = json.dumps(data["related_slugs"], ensure_ascii=False)


@router.get("", response_model=list[ProjectOut])
def public_projects(db: Session = Depends(get_db)):
    items = db.scalars(select(Project).where(Project.is_visible.is_(True)).order_by(Project.is_featured.desc(), Project.sort_order, Project.id)).all()
    return [_payload(item) for item in items]


@router.get("/{slug}", response_model=ProjectOut)
def public_project(slug: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Project).where(Project.slug == slug, Project.is_visible.is_(True)))
    if not item:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    return _payload(item)


@admin_router.get("", response_model=list[ProjectOut])
def admin_projects(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    items = db.scalars(select(Project).order_by(Project.sort_order, Project.id)).all()
    return [_payload(item) for item in items]


@admin_router.post("", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(Project).where(Project.slug == data.slug)):
        raise HTTPException(status_code=409, detail="معرّف المشروع مستخدم مسبقاً")
    item = Project()
    _apply(item, data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _payload(item)


@admin_router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Project, project_id)
    if not item:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    _apply(item, data.model_dump(exclude_unset=True))
    db.commit()
    db.refresh(item)
    return _payload(item)


@admin_router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, confirm: bool = False, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if not confirm:
        raise HTTPException(status_code=400, detail="يتطلب الحذف تأكيداً صريحاً")
    item = db.get(Project, project_id)
    if not item:
        raise HTTPException(status_code=404, detail="المشروع غير موجود")
    db.delete(item)
    db.commit()


@admin_router.post("/media", status_code=201)
async def upload_project_media(request: Request, filename: str, _: User = Depends(require_admin)):
    suffix = Path(filename).suffix.lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm"}
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="نوع الوسائط غير مسموح")
    safe_name = f"{uuid4().hex}{suffix}"
    root = Path(__file__).resolve().parents[2] / "public" / "uploads" / "projects"
    root.mkdir(parents=True, exist_ok=True)
    destination = root / safe_name
    data = await request.body()
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="حجم الملف أكبر من 12MB")
    destination.write_bytes(data)
    return {"url": f"/uploads/projects/{safe_name}", "filename": safe_name}
