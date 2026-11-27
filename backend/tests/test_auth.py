import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.db.models import User, UserToken
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


def _clear_user(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user:
            db.query(UserToken).filter_by(user_id=user.id).delete()
            db.query(User).filter_by(email=email).delete()
            db.commit()
    finally:
        db.close()


def test_auth_flow_register_login_refresh_logout():
    email = "tdd-auth@example.com"
    _clear_user(email)

    r = client.post("/api/v1/auth/register", json={"name": "TDD", "email": email, "password": "Secret@123"})
    assert r.status_code == 201, r.text

    dup = client.post("/api/v1/auth/register", json={"name": "TDD", "email": email, "password": "Secret@123"})
    assert dup.status_code == 409

    r = client.post("/api/v1/auth/login", json={"email": email, "password": "Secret@123"})
    assert r.status_code == 200, r.text
    pair = r.json()["data"]
    assert pair["token_type"] == "Bearer" and pair["expires_in"] == 30

    bad = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert bad.status_code == 401

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": pair["refresh_token"]})
    assert r.status_code == 200, r.text
    pair2 = r.json()["data"]

    reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": pair["refresh_token"]})
    assert reuse.status_code == 401

    r = client.post("/api/v1/auth/logout", json={"refresh_token": pair2["refresh_token"]})
    assert r.status_code == 200

    after = client.post("/api/v1/auth/refresh", json={"refresh_token": pair2["refresh_token"]})
    assert after.status_code == 401

    _clear_user(email)


def test_validation_error_shape_has_no_input():
    r = client.post("/api/v1/auth/register", json={"name": "", "email": "not-an-email", "password": "x"})
    assert r.status_code == 400
    body = r.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert all("input" not in d and "ctx" not in d for d in body["error"]["details"])
