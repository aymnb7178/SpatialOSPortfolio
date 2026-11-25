import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

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
from backend.app.routers.auth import _auth_attempts
from backend.app.routers.messages import _message_attempts
from backend.app.schemas import PaymentCreate, SiteLinkCreate

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
