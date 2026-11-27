import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.db.models import Rating, User, UserToken
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)

EMAIL = "tdd-interaction@example.com"


def _auth_headers() -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=EMAIL).first()
        if user:
            db.query(Rating).filter_by(user_id=user.id).delete()
            db.query(UserToken).filter_by(user_id=user.id).delete()
            db.delete(user)
            db.commit()
    finally:
        db.close()
    r = client.post("/api/v1/auth/register", json={"name": "TDD", "email": EMAIL, "password": "Secret@123"})
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "Secret@123"})
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_favorite_idempotent_and_list():
    h = _auth_headers()

    anon = client.post("/api/v1/me/favorites/1")
    assert anon.status_code == 401

    r = client.post("/api/v1/me/favorites/1", headers=h)
    assert r.status_code == 200, r.text
    again = client.post("/api/v1/me/favorites/1", headers=h)
    assert again.status_code == 200

    r = client.get("/api/v1/me/favorites", headers=h)
    assert r.status_code == 200
    assert any(d["id"] == 1 for d in r.json()["data"])

    r = client.delete("/api/v1/me/favorites/1", headers=h)
    assert r.status_code == 200
    r = client.get("/api/v1/me/favorites", headers=h)
    assert all(d["id"] != 1 for d in r.json()["data"])

    missing = client.post("/api/v1/me/favorites/999999", headers=h)
    assert missing.status_code == 404


def test_rating_upsert_recomputes_avg_and_get_null():
    h = _auth_headers()

    r = client.get("/api/v1/me/ratings/2", headers=h)
    assert r.status_code == 200
    assert r.json()["data"] is None

    r = client.put("/api/v1/me/ratings/2", json={"rating_score": 5, "comment": "Tuyệt vời"}, headers=h)
    assert r.status_code == 200, r.text

    bad = client.put("/api/v1/me/ratings/2", json={"rating_score": 9}, headers=h)
    assert bad.status_code == 400

    r = client.put("/api/v1/me/ratings/2", json={"rating_score": 4}, headers=h)
    assert r.json()["data"]["rating_score"] == 4

    detail = client.get("/api/v1/destinations/2")
    assert detail.json()["data"]["rating_avg"] == 4.0
    assert detail.json()["data"]["metrics"]["rating_count"] >= 1
