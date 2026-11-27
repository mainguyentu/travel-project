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

USER_EMAIL = "tdd-admin-user@example.com"
TARGET_EMAIL = "tdd-admin-target@example.com"


def _login(email: str, password: str) -> dict:
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _reset_user(email: str, role: str = "user") -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user:
            db.query(Rating).filter_by(user_id=user.id).delete()
            db.query(UserToken).filter_by(user_id=user.id).delete()
            db.delete(user)
            db.commit()
        r = client.post(
            "/api/v1/auth/register",
            json={"name": "TDD", "email": email, "password": "Secret@123"},
        )
        assert r.status_code == 201, r.text
        if role == "admin":
            admin = _login("admin@alats.vn", "Admin@123")
            db2 = SessionLocal()
            try:
                target = db2.query(User).filter_by(email=email).first()
                tid = target.id
            finally:
                db2.close()
            rr = client.patch(f"/api/v1/admin/users/{tid}/role", json={"role": "admin"}, headers=admin)
            assert rr.status_code == 200, rr.text
    finally:
        db.close()


def test_admin_guard_and_users_flow():
    _reset_user(USER_EMAIL)
    _reset_user(TARGET_EMAIL)
    admin = _login("admin@alats.vn", "Admin@123")
    user = _login(USER_EMAIL, "Secret@123")

    # non-admin denied
    r = client.get("/api/v1/admin/users", headers=user)
    assert r.status_code == 403

    # list
    r = client.get("/api/v1/admin/users", headers=admin)
    assert r.status_code == 200, r.text
    assert r.json()["meta"]["total"] >= 2

    db = SessionLocal()
    try:
        target = db.query(User).filter_by(email=TARGET_EMAIL).first()
        tid = target.id
    finally:
        db.close()

    # lock -> locked user cannot use token (login taken before lock)
    target_headers = _login(TARGET_EMAIL, "Secret@123")
    r = client.patch(f"/api/v1/admin/users/{tid}/status", json={"status": "locked"}, headers=admin)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "locked"

    r = client.get("/api/v1/me/favorites", headers=target_headers)
    assert r.status_code == 403

    # locked user cannot login again
    bad_login = client.post("/api/v1/auth/login", json={"email": TARGET_EMAIL, "password": "Secret@123"})
    assert bad_login.status_code == 403

    r = client.patch(f"/api/v1/admin/users/{tid}/status", json={"status": "active"}, headers=admin)
    assert r.status_code == 200

    # bad status value
    r = client.patch(f"/api/v1/admin/users/{tid}/status", json={"status": "bogus"}, headers=admin)
    assert r.status_code == 400

    # missing user
    r = client.patch("/api/v1/admin/users/999999/status", json={"status": "locked"}, headers=admin)
    assert r.status_code == 404


def test_admin_categories_crud():
    _reset_user(USER_EMAIL)
    admin = _login("admin@alats.vn", "Admin@123")

    r = client.post(
        "/api/v1/admin/categories",
        json={"name": "TDD Cat", "slug": "tdd-cat", "descriptions": "x"},
        headers=admin,
    )
    assert r.status_code == 201, r.text
    cid = r.json()["data"]["id"]

    dup = client.post(
        "/api/v1/admin/categories",
        json={"name": "Dup", "slug": "tdd-cat"},
        headers=admin,
    )
    assert dup.status_code == 409

    r = client.put(f"/api/v1/admin/categories/{cid}", json={"name": "TDD Cat 2"}, headers=admin)
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "TDD Cat 2"

    r = client.delete(f"/api/v1/admin/categories/{cid}", headers=admin)
    assert r.status_code == 200

    r = client.delete(f"/api/v1/admin/categories/{cid}", headers=admin)
    assert r.status_code == 404


def _cleanup_slug(slug: str, headers: dict) -> None:
    db = SessionLocal()
    try:
        from app.db.models import CategoryDestination, Destination, DestinationInsight
        dest = db.query(Destination).filter_by(slug=slug).first()
        if dest:
            db.query(CategoryDestination).filter_by(destination_id=dest.id).delete()
            db.query(DestinationInsight).filter_by(destination_id=dest.id).delete()
            db.delete(dest)
            db.commit()
    finally:
        db.close()


def test_admin_destinations_crud_and_stats():
    import time, uuid
    _reset_user(USER_EMAIL)
    admin = _login("admin@alats.vn", "Admin@123")
    user = _login(USER_EMAIL, "Secret@123")
    suffix = uuid.uuid4().hex[:8]
    slug = f"tdd-island-{suffix}"

    r = client.post(
        "/api/v1/admin/destinations",
        json={
            "name": "TDD Island",
            "slug": slug,
            "price_level": "low",
            "category_slugs": ["bien"],
        },
        headers=admin,
    )
    assert r.status_code == 201, r.text
    did = r.json()["data"]["id"]

    bad_cat = client.post(
        "/api/v1/admin/destinations",
        json={"name": "Bad", "slug": "tdd-bad", "category_slugs": ["nope"]},
        headers=admin,
    )
    assert bad_cat.status_code == 400

    # non-admin cannot create
    r = client.post(
        "/api/v1/admin/destinations",
        json={"name": "No", "slug": "tdd-no"},
        headers=user,
    )
    assert r.status_code == 403

    r = client.put(f"/api/v1/admin/destinations/{did}", json={"price_level": "medium"}, headers=admin)
    assert r.status_code == 200
    assert r.json()["data"]["price_level"] == "medium"

    r = client.get("/api/v1/destinations/search", params={"q": "TDD Island"})
    assert any(d["slug"] == slug for d in r.json()["data"])

    for path in ("top-favorites", "top-ratings", "top-views"):
        r = client.get(f"/api/v1/admin/stats/{path}", headers=admin)
        assert r.status_code == 200, r.text
        assert isinstance(r.json()["data"], list)

    r = client.delete(f"/api/v1/admin/destinations/{did}", headers=admin)
    assert r.status_code == 200
    r = client.delete(f"/api/v1/admin/destinations/{did}", headers=admin)
    assert r.status_code == 404
