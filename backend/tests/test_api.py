from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import AuditLog, Category, CategoryDestination, Destination, User
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)


def seed_basic():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@alats.vn").first()
        if not admin:
            admin = User(name="Admin", email="admin@alats.vn", password_hash=hash_password("Admin@123"), role="admin", status="active")
            db.add(admin)
        user = db.query(User).filter(User.email == "user@alats.vn").first()
        if not user:
            user = User(name="User", email="user@alats.vn", password_hash=hash_password("User@123"), role="user", status="active")
            db.add(user)
        category = db.query(Category).filter(Category.slug == "beach").first()
        if not category:
            category = Category(name="Bai bien", slug="beach", descriptions="Cac bai bien dep")
            db.add(category)
        db.flush()
        destination = db.query(Destination).filter(Destination.slug == "my-khe-beach").first()
        if not destination:
            destination = Destination(
                name="My Khe Beach",
                slug="my-khe-beach",
                address="Vo Nguyen Giap, Da Nang",
                description="Bai bien noi tieng",
                price_level="free",
                open_hour="All day",
                status="active",
            )
            db.add(destination)
            db.flush()
            db.add(CategoryDestination(category_id=category.id, destination_id=destination.id))
        db.commit()
        return admin.email, user.email, category.id, destination.id
    finally:
        db.close()


def login(email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["data"]["access_token"]


def create_user(email: str, password: str = "User@123", role: str = "user", status: str = "active"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            existing.password_hash = hash_password(password)
            existing.role = role
            existing.status = status
            user = existing
        else:
            user = User(
                name=email.split("@")[0],
                email=email,
                password_hash=hash_password(password),
                role=role,
                status=status,
            )
            db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def test_auth_register_login_refresh_logout():
    email = f"newuser-{uuid4().hex[:8]}@alats.vn"
    resp = client.post("/api/v1/auth/register", json={"name": "New", "email": email, "password": "User@123"})
    assert resp.status_code in (200, 201)

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "User@123"})
    assert login_resp.status_code == 200
    tokens = login_resp.json()["data"]

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 200

    logout_resp = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_resp.status_code == 200

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        actions = (
            db.query(AuditLog)
            .filter(AuditLog.actor_user_id == user.id)
            .order_by(AuditLog.id.asc())
            .all()
        )
        action_names = [a.action for a in actions]
        assert "auth.register" in action_names
        assert "auth.login" in action_names
        assert "auth.refresh" in action_names
        assert "auth.logout" in action_names
    finally:
        db.close()


def test_auth_refresh_revoked_token_rejected():
    email = f"revoke-{uuid4().hex[:8]}@alats.vn"
    create_user(email=email, password="User@123")

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "User@123"})
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["data"]["refresh_token"]

    logout_resp = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 200

    refresh_again = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_again.status_code == 401
    assert refresh_again.json()["error"]["code"] == "UNAUTHORIZED"


def test_auth_invalid_credentials():
    create_user(email=f"invalid-{uuid4().hex[:8]}@alats.vn", password="User@123")
    resp = client.post("/api/v1/auth/login", json={"email": "unknown@alats.vn", "password": "WrongPass@123"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_auth_locked_user_login_forbidden():
    email = f"locked-{uuid4().hex[:8]}@alats.vn"
    create_user(email=email, password="User@123", status="locked")

    resp = client.post("/api/v1/auth/login", json={"email": email, "password": "User@123"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_auth_refresh_for_locked_user_forbidden():
    email = f"refresh-locked-{uuid4().hex[:8]}@alats.vn"
    create_user(email=email, password="User@123", status="active")

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "User@123"})
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["data"]["refresh_token"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        user.status = "locked"
        db.commit()
    finally:
        db.close()

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 403
    assert refresh_resp.json()["error"]["code"] == "FORBIDDEN"


def test_auth_expired_refresh_token_rejected():
    expired_refresh = jwt.encode(
        {
            "sub": "1",
            "iss": settings.jwt_issuer,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "type": "refresh",
        },
        settings.jwt_secret,
        algorithm="HS256",
    )

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_refresh})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_public_and_destinations():
    _, _, _, destination_id = seed_basic()

    landing = client.get("/api/v1/public/landing")
    assert landing.status_code == 200

    listing = client.get("/api/v1/destinations", params={"page": 1, "limit": 5})
    assert listing.status_code == 200
    assert isinstance(listing.json()["data"], list)

    detail = client.get(f"/api/v1/destinations/{destination_id}")
    assert detail.status_code == 200


def test_interaction_flow():
    _, user_email, _, destination_id = seed_basic()
    token = login(user_email, "User@123")

    fav = client.post(f"/api/v1/me/favorites/{destination_id}", headers={"Authorization": f"Bearer {token}"})
    assert fav.status_code == 200

    fav_list = client.get("/api/v1/me/favorites", headers={"Authorization": f"Bearer {token}"})
    assert fav_list.status_code == 200

    rating = client.put(
        f"/api/v1/me/ratings/{destination_id}",
        json={"rating_score": 5, "comment": "Great"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert rating.status_code == 200

    my_rating = client.get(f"/api/v1/me/ratings/{destination_id}", headers={"Authorization": f"Bearer {token}"})
    assert my_rating.status_code == 200

    unfav = client.delete(f"/api/v1/me/favorites/{destination_id}", headers={"Authorization": f"Bearer {token}"})
    assert unfav.status_code == 200


def test_interaction_requires_auth_header():
    _, _, _, destination_id = seed_basic()
    resp = client.post(f"/api/v1/me/favorites/{destination_id}")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


def test_interaction_favorite_is_idempotent():
    _, user_email, _, destination_id = seed_basic()
    token = login(user_email, "User@123")
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(f"/api/v1/me/favorites/{destination_id}", headers=headers)
    second = client.post(f"/api/v1/me/favorites/{destination_id}", headers=headers)
    listed = client.get("/api/v1/me/favorites", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert listed.status_code == 200
    ids = [item["id"] for item in listed.json()["data"]]
    assert ids.count(destination_id) == 1


def test_interaction_unfavorite_is_idempotent():
    _, user_email, _, destination_id = seed_basic()
    token = login(user_email, "User@123")
    headers = {"Authorization": f"Bearer {token}"}

    _ = client.post(f"/api/v1/me/favorites/{destination_id}", headers=headers)
    first = client.delete(f"/api/v1/me/favorites/{destination_id}", headers=headers)
    second = client.delete(f"/api/v1/me/favorites/{destination_id}", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200


def test_admin_flow():
    admin_email, _, _, _ = seed_basic()
    token = login(admin_email, "Admin@123")

    cat = client.post(
        "/api/v1/admin/categories",
        json={"name": "Am thuc", "slug": "food", "descriptions": "Quan an"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cat.status_code in (200, 201, 409)

    stats = client.get("/api/v1/admin/stats/top-views", headers={"Authorization": f"Bearer {token}"})
    assert stats.status_code == 200

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == admin_email).first()
        assert admin is not None
        actions = (
            db.query(AuditLog)
            .filter(AuditLog.actor_user_id == admin.id)
            .order_by(AuditLog.id.asc())
            .all()
        )
        action_names = [a.action for a in actions]
        assert "admin.category.create" in action_names
    finally:
        db.close()


def test_admin_forbidden_for_non_admin_user():
    _, user_email, _, _ = seed_basic()
    token = login(user_email, "User@123")
    resp = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "FORBIDDEN"


def test_admin_category_duplicate_slug_conflict():
    admin_email, _, _, _ = seed_basic()
    token = login(admin_email, "Admin@123")
    headers = {"Authorization": f"Bearer {token}"}

    slug = f"dup-{uuid4().hex[:8]}"
    first = client.post(
        "/api/v1/admin/categories",
        json={"name": "Dup 1", "slug": slug, "descriptions": "First"},
        headers=headers,
    )
    second = client.post(
        "/api/v1/admin/categories",
        json={"name": "Dup 2", "slug": slug, "descriptions": "Second"},
        headers=headers,
    )

    assert first.status_code in (200, 201)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CONFLICT"
