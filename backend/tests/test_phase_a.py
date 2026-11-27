import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.db.models import User
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)
INTERNAL_HEADERS = {"X-Internal-Key": "dev-internal-key"}


def _login(email: str, password: str) -> dict:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_bulk_create_idempotent_guards():
    import time
    admin = _login("admin@alats.vn", "Admin@123")
    suffix = str(int(time.time() % 1000000))
    s1, s2 = f"pha-a-bulk-1-{suffix}", f"pha-a-bulk-2-{suffix}"
    # duplicate slug inside payload -> 400
    r = client.post(
        "/api/v1/admin/destinations/bulk",
        json={"items": [
            {"name": "Bulk A", "slug": f"bulk-dup-{suffix}"},
            {"name": "Bulk A2", "slug": f"bulk-dup-{suffix}"},
        ]},
        headers=admin,
    )
    assert r.status_code == 400, r.text
    # valid bulk -> 201
    r = client.post(
        "/api/v1/admin/destinations/bulk",
        json={"items": [
            {"name": "Bulk One", "slug": s1, "price_level": "free"},
            {"name": "Bulk Two", "slug": s2, "price_level": "low"},
        ]},
        headers=admin,
    )
    assert r.status_code == 201, r.text
    assert len(r.json()["data"]) == 2
    # same slugs again -> 409
    r = client.post(
        "/api/v1/admin/destinations/bulk",
        json={"items": [{"name": "Bulk One", "slug": s1}]},
        headers=admin,
    )
    assert r.status_code == 409, r.text
    # audit log recorded
    r = client.get("/api/v1/admin/audit-logs", headers=admin)
    assert r.status_code == 200, r.text
    actions = [row["action"] for row in r.json()["data"]]
    assert "bulk_create" in actions


def test_analytics_require_admin_and_time_filter():
    # no token -> 401
    r = client.get("/api/v1/analytics/summary")
    assert r.status_code == 401
    # user token -> 403
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email="user@alats.vn").first()
        assert user is not None
    finally:
        db.close()
    user_h = _login("user@alats.vn", "User@123")
    r = client.get("/api/v1/analytics/summary", headers=user_h)
    assert r.status_code == 403
    # admin ok + time filter params accepted
    admin = _login("admin@alats.vn", "Admin@123")
    r = client.get("/api/v1/analytics/summary", headers=admin)
    assert r.status_code == 200, r.text
    assert "total_destinations" in r.json()["data"]
    r = client.get(
        "/api/v1/analytics/top-favorites",
        params={"limit": 5, "from": "2020-01-01T00:00:00Z", "to": "2030-01-01T00:00:00Z"},
        headers=admin,
    )
    assert r.status_code == 200, r.text
    # limit bound enforced
    r = client.get("/api/v1/analytics/top-favorites", params={"limit": 200}, headers=admin)
    assert r.status_code == 400


def test_internal_key_and_activities():
    # wrong key -> 401
    r = client.get("/api/v1/internal/destinations/1/active", headers={"X-Internal-Key": "wrong"})
    assert r.status_code == 401
    # right key
    r = client.get("/api/v1/internal/destinations/1/active", headers=INTERNAL_HEADERS)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["active"] is True
    r = client.post("/api/v1/internal/destinations/batch", json={"ids": [1, 2]}, headers=INTERNAL_HEADERS)
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["data"], list)
    r = client.post("/api/v1/internal/destinations/1/recompute-rating-avg", headers=INTERNAL_HEADERS)
    assert r.status_code == 200, r.text
    assert "rating_avg" in r.json()["data"]
    # activities recommendations
    r = client.get("/api/v1/public/activities/bien/recommendations")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert "recommended_destinations" in data and "activity" in data
    # unknown activity -> 404
    r = client.get("/api/v1/public/activities/nope-x/recommendations")
    assert r.status_code == 404
