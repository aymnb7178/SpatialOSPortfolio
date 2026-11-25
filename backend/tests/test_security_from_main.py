import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/spatialos-main-audit-test.db")
os.environ.setdefault("ADMIN_EMAIL", "admin@example.com")
os.environ.setdefault("MOYASAR_WEBHOOK_SECRET", "")

from backend.app.config import Settings, get_settings
from backend.app.database import Base, engine, get_db
from backend.app.main import app
from backend.app.moyasar import create_payment
from backend.app.models import User
from backend.app.routers.auth import _auth_attempts
from backend.app.routers.messages import _message_attempts
from backend.app.schemas import GithubRepositoryAdminUpdate, PaymentCreate, ProjectCreate, SiteLinkCreate

Path("/tmp/spatialos-main-audit-test.db").unlink(missing_ok=True)
Base.metadata.create_all(engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client
    _auth_attempts.clear()
    _message_attempts.clear()


def test_registration_never_grants_admin_by_email(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Normal User", "email": "admin@example.com", "password": "safe-password-123"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_admin_login_cookie_session_and_logout():
    from backend.app.auth import hash_password
    from backend.app.config import get_settings

    settings = get_settings()
    previous_admin_email = settings.admin_email
    settings.admin_email = "admin-login@example.com"
    db = next(get_db())
    try:
        admin = db.scalar(select(User).where(User.email == settings.admin_email))
        if not admin:
            admin = User(name="Test Admin", email=settings.admin_email, password_hash=hash_password("Admin-safe-123"), role="admin")
            db.add(admin)
            db.commit()
        with TestClient(app) as admin_client:
            response = admin_client.post("/api/auth/login", json={"email": settings.admin_email, "password": "Admin-safe-123"})
            assert response.status_code == 200
            assert response.json()["role"] == "admin"
            assert "access_token=" in response.headers.get("set-cookie", "")
            assert admin_client.get("/api/auth/me").status_code == 200
            assert admin_client.get("/api/admin/summary").status_code == 200
            assert admin_client.post("/api/auth/logout").status_code == 204
            assert admin_client.get("/api/auth/me").status_code == 401
    finally:
        settings.admin_email = previous_admin_email
        db.close()


def test_payment_schema_rejects_amount_and_card_fields():
    with pytest.raises(ValidationError):
        PaymentCreate.model_validate(
            {
                "order_id": 1,
                "amount": 100,
                "card_number": "4111111111111111",
                "card_cvc": "123",
            }
        )


def test_webhook_requires_secret_and_admin_requires_auth(client):
    webhook = client.post("/api/payments/webhook", json={"type": "payment_failed"})
    admin = client.get("/api/admin/summary")
    assert webhook.status_code == 503
    assert admin.status_code == 403
    with TestClient(app) as anonymous:
        assert anonymous.get("/api/admin/summary").status_code == 401


def test_career_and_skills_public_endpoints_and_admin_boundary(client):
    assert client.get("/api/career").status_code == 200
    assert client.get("/api/skills").status_code == 200
    assert client.get("/api/admin/career").status_code == 403
    assert client.get("/api/admin/skills").status_code == 403
    with TestClient(app) as anonymous:
        assert anonymous.get("/api/admin/career").status_code == 401
        assert anonymous.get("/api/admin/skills").status_code == 401


def test_webhook_rejects_wrong_secret_and_moyasar_stub_is_disabled(client):
    settings = get_settings()
    previous = settings.moyasar_webhook_secret
    settings.moyasar_webhook_secret = "test-secret"
    try:
        response = client.post(
            "/api/payments/webhook",
            json={"secret_token": "wrong", "type": "payment_failed"},
        )
        assert response.status_code == 401
    finally:
        settings.moyasar_webhook_secret = previous

    import asyncio
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as error:
        asyncio.run(create_payment())
    assert error.value.status_code == 409


def test_origin_and_body_size_protection(client):
    origin = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "not-used"},
        headers={"origin": "https://evil.example"},
    )
    oversized = client.post(
        "/api/auth/login",
        content=b"x" * (1_048_576 + 1),
        headers={"content-type": "application/json"},
    )
    assert origin.status_code == 403
    assert oversized.status_code == 413


def test_admin_link_schema_rejects_unsafe_url():
    with pytest.raises(ValidationError):
        SiteLinkCreate.model_validate({"label": "bad", "url": "javascript:alert(1)"})


def test_production_defaults_are_rejected():
    with pytest.raises(ValueError):
        Settings(app_env="production", jwt_secret="change-me-in-production", cookie_secure=False, admin_email="admin@example.com")


def test_static_assets_receive_cache_headers_without_caching_html_or_api(client):
    asset = client.get("/fonts/thmanyah/thmanyahsans-Regular.woff2")
    html = client.get("/")
    api = client.get("/health")
    assert asset.status_code == 200
    assert asset.headers["cache-control"].startswith("public, max-age=604800")
    assert "cache-control" not in html.headers
    assert "cache-control" not in api.headers


def test_project_public_api_and_admin_boundary(client):
    assert client.get("/api/projects").status_code == 200
    assert client.get("/api/projects/missing").status_code == 404
    assert client.get("/api/admin/projects").status_code == 403
    with TestClient(app) as anonymous:
        assert anonymous.get("/api/admin/projects").status_code == 401


def test_project_schema_rejects_unsafe_urls_and_invalid_slug():
    with pytest.raises(ValidationError):
        ProjectCreate(slug="Bad Slug", title="Project", github_url="javascript:alert(1)")


def test_github_public_overview_cache_details_and_admin_boundary(client, monkeypatch):
    import backend.app.routers.github as github_router

    class FakeGithubClient:
        calls = 0
        username = "aymnb7178"
        remaining = 4900
        reset_at = None

        def profile(self):
            type(self).calls += 1
            return {"login": "aymnb7178", "name": "Eng.AIMAN AL ERWI", "avatar_url": "https://avatars.githubusercontent.com/u/208697478?v=4", "html_url": "https://github.com/aymnb7178", "bio": "", "public_repos": 1, "followers": 1, "following": 0, "public_gists": 0}

        def repos(self):
            type(self).calls += 1
            return [{"id": 77, "name": "demo-repo", "full_name": "aymnb7178/demo-repo", "description": "A public demo", "html_url": "https://github.com/aymnb7178/demo-repo", "language": "Python", "stargazers_count": 3, "forks_count": 1, "watchers_count": 3, "open_issues_count": 0, "size": 10, "default_branch": "main", "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-02T00:00:00Z", "pushed_at": "2026-01-02T00:00:00Z", "archived": False, "fork": False, "topics": []}]

        def events(self):
            type(self).calls += 1
            return [{"id": "e1", "type": "PushEvent", "repo": {"name": "aymnb7178/demo-repo"}, "actor": {"login": "aymnb7178"}, "created_at": "2026-01-02T00:00:00Z", "public": True}]

        def languages(self, full_name):
            type(self).calls += 1
            return {"Python": 1000, "HTML": 250}

        def readme(self, full_name):
            return "# Demo README\n\nSafe text"

    monkeypatch.setattr(github_router, "GithubClient", FakeGithubClient)
    first = client.get("/api/github/overview")
    assert first.status_code == 200
    assert first.json()["profile"]["login"] == "aymnb7178"
    assert first.json()["profile"]["stars"] == 3
    assert first.json()["repositories"][0]["name"] == "demo-repo"
    calls_after_first = FakeGithubClient.calls
    second = client.get("/api/github/repos?q=demo&language=Python&sort=stars")
    assert second.status_code == 200
    assert second.json()[0]["languages"]["Python"] == 1000
    assert FakeGithubClient.calls == calls_after_first
    detail = client.get("/api/github/repos/demo-repo")
    assert detail.status_code == 200
    assert "Demo README" in detail.json()["readme_markdown"]
    assert client.get("/api/admin/github/repos").status_code == 403
    assert GithubRepositoryAdminUpdate.model_validate({"is_featured": True, "sort_order": 2})


def test_github_fallback_uses_stale_cache_on_rate_limit(client, monkeypatch):
    import backend.app.routers.github as github_router

    class RateLimitedClient:
        username = "aymnb7178"
        remaining = 0
        reset_at = None

        def profile(self):
            raise github_router.GithubRemoteError("rate limited", 429)

    monkeypatch.setattr(github_router, "GithubClient", RateLimitedClient)
    monkeypatch.setattr(github_router, "_fresh", lambda state: False)
    response = client.get("/api/github/overview")
    assert response.status_code == 200
    assert response.json()["repositories"][0]["name"] == "demo-repo"
