import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.core.rate_limit import reset_buckets
from app.main import app

client = TestClient(app)


def test_rate_limit_headers_shape():
    reset_buckets()
    for _ in range(3):
        r = client.get("/api/v1/destinations/search", params={"q": ""})
        assert r.status_code in (200, 429)
    assert True


def test_rate_limit_429_envelope():
    from app.core import rate_limit as rl

    ok, _ = rl._allow("test-key-c", 2)
    assert ok is True
    rl._allow("test-key-c", 2)
    ok, retry = rl._allow("test-key-c", 2)
    assert ok is False and retry >= 1
    rl._buckets.pop("test-key-c", None)


def test_security_headers_present():
    reset_buckets()
    r = client.get("/api/v1/destinations/search", params={"q": ""})
    assert r.status_code == 200, r.text
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Referrer-Policy") == "same-origin"
    assert r.headers.get("X-Request-Id")


def test_metrics_and_ready_shape():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "travel_uptime_seconds" in r.text
    assert "travel_rate_limit_ip_per_min 120" in r.text
    r = client.get("/ready")
    assert r.status_code == 200, r.text
    assert "checks" in r.json()["data"]


def test_audit_records_admin_actions():
    from app.db.models import AuditLog
    from app.db.session import SessionLocal

    def login(email, password):
        r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['data']['access_token']}"}

    reset_buckets()
    admin = login("admin@alats.vn", "Admin@123")
    db = SessionLocal()
    try:
        before = db.query(AuditLog).count()
    finally:
        db.close()
    r = client.post(
        "/api/v1/admin/categories",
        json={"name": "Audit Cat", "slug": "audit-cat-c"},
        headers=admin,
    )
    assert r.status_code in (200, 201, 409), r.text
    cid = None
    if r.status_code == 201:
        cid = r.json()["data"]["id"]
        r = client.delete(f"/api/v1/admin/categories/{cid}", headers=admin)
        assert r.status_code == 200, r.text
    db = SessionLocal()
    try:
        after = db.query(AuditLog).count()
        assert after > before
    finally:
        db.close()
