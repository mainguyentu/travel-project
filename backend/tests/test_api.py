from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import AuditLog, Category, CategoryDestination, Destination, DestinationInsight, User
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
    payload = detail.json()["data"]
    assert "insight" in payload
    assert "metrics" in payload


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


def test_admin_destination_list_and_create():
    admin_email, _, category_id, _ = seed_basic()
    token = login(admin_email, "Admin@123")
    headers = {"Authorization": f"Bearer {token}"}

    listed = client.get("/api/v1/admin/destinations", headers=headers)
    assert listed.status_code == 200
    assert isinstance(listed.json()["data"], list)

    slug = f"admin-destination-{uuid4().hex[:8]}"
    create_resp = client.post(
        "/api/v1/admin/destinations",
        headers=headers,
        json={
            "name": "Admin Destination",
            "slug": slug,
            "address": "Da Nang",
            "description": "Created from admin endpoint",
            "price_level": "medium",
            "open_hour": "All day",
            "img_url": "https://example.com/admin-destination.jpg",
            "url_map": "https://maps.google.com",
            "lat": 16.047079,
            "lng": 108.20623,
            "status": "active",
            "category_ids": [category_id],
        },
    )
    assert create_resp.status_code in (200, 201)

    admin_list = client.get("/api/v1/admin/destinations", headers=headers)
    assert admin_list.status_code == 200
    assert any(item["slug"] == slug for item in admin_list.json()["data"])


def test_admin_destination_single_create_autogenerates_slug():
    admin_email, _, category_id, _ = seed_basic()
    token = login(admin_email, "Admin@123")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/api/v1/admin/destinations",
        headers=headers,
        json={
            "name": "Bảo tàng 3D Art In Paradise",
            "address": "Da Nang",
            "description": "Created without slug",
            "price_level": "medium",
            "open_hour": "All day",
            "img_url": "https://example.com/admin-destination.jpg",
            "url_map": "https://maps.google.com",
            "lat": 16.047079,
            "lng": 108.20623,
            "status": "active",
            "category_ids": [category_id],
        },
    )
    assert create_resp.status_code in (200, 201)
    data = create_resp.json()["data"]
    assert data["slug"]
    assert data["slug"].startswith("bao-tang-3d-art-in-paradise")


def test_admin_destination_bulk_create():
    admin_email, _, category_id, _ = seed_basic()
    token = login(admin_email, "Admin@123")
    headers = {"Authorization": f"Bearer {token}"}

    slug_a = f"bulk-destination-a-{uuid4().hex[:8]}"
    slug_b = f"bulk-destination-b-{uuid4().hex[:8]}"

    existing_category_name = "Điểm thu hút khách du lịch"
    db = SessionLocal()
    try:
        existing = db.query(Category).filter(Category.name == existing_category_name).first()
        if not existing:
            db.add(Category(name=existing_category_name, slug=f"tourist-spot-{uuid4().hex[:6]}", descriptions="Existing"))
            db.commit()
    finally:
        db.close()

    create_resp = client.post(
        "/api/v1/admin/destinations/bulk",
        headers=headers,
        json={
            "destinations": [
                {
                    "name": "Bulk Destination A",
                    "address": "Da Nang",
                    "description": "Bulk create A",
                    "rating": 4.4,
                    "price": "333.920 ₫",
                    "open_hour": "All day",
                    "image": ["https://example.com/bulk-a.jpg"],
                    "maps_url": "https://maps.google.com",
                    "lat": 16.047079,
                    "lng": 108.20623,
                    "status": "active",
                    "category_ids": [category_id],
                    "category": [existing_category_name, "Bảo tàng"],
                    "reviews": [
                        {
                            "author": "A",
                            "rating": 5,
                            "text": "Phong cảnh đẹp, giá hợp lý",
                        },
                        {
                            "author": "B",
                            "rating": 4,
                            "text": "Hơi đông nhưng đi lại thuận tiện",
                        },
                    ],
                },
                {
                    "name": "Bulk Destination B",
                    "address": "Hue",
                    "description": "Bulk create B",
                    "price_level": "high",
                    "open_hour": "08:00-22:00",
                    "img_url": "https://example.com/bulk-b.jpg",
                    "url_map": "https://maps.google.com",
                    "lat": 16.4637,
                    "lng": 107.5909,
                    "status": "active",
                    "category_ids": [category_id],
                },
            ]
        },
    )
    assert create_resp.status_code in (200, 201)
    assert create_resp.json()["meta"]["count"] == 2

    created_payload = create_resp.json()["data"]
    created_slugs = [item["slug"] for item in created_payload]
    assert len(created_slugs) == 2
    assert all(created_slugs)
    assert len(set(created_slugs)) == 2

    admin_list = client.get("/api/v1/admin/destinations", headers=headers)
    assert admin_list.status_code == 200
    slugs = [item["slug"] for item in admin_list.json()["data"]]
    assert all(slug in slugs for slug in created_slugs)

    db = SessionLocal()
    try:
        created_a = db.query(Destination).filter(Destination.slug == created_slugs[0]).first()
        assert created_a is not None
        assert float(created_a.rating_avg or 0) == 4.4
        assert created_a.price_raw_text == "333.920 ₫"

        category_names = [link.category.name for link in created_a.categories]
        assert existing_category_name in category_names
        assert "Bảo tàng" in category_names

        duplicate_existing = db.query(Category).filter(Category.name == existing_category_name).count()
        assert duplicate_existing == 1

        insight = db.query(DestinationInsight).filter(DestinationInsight.destination_id == created_a.id).first()
        assert insight is not None
        assert insight.final_data is not None
        assert insight.final_data.get("status") in ("low_confidence", "reliable", "insufficient_data")
        assert isinstance((insight.insight_cache or {}).get("total_reviews", 0), int)
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
