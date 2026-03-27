from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models import User, Category, Destination, CategoryDestination
from app.core.security import hash_password

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


def test_auth_register_login_refresh_logout():
    email = "newuser@alats.vn"
    resp = client.post("/api/v1/auth/register", json={"name": "New", "email": email, "password": "User@123"})
    assert resp.status_code in (200, 201)

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "User@123"})
    assert login_resp.status_code == 200
    tokens = login_resp.json()["data"]

    refresh_resp = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh_resp.status_code == 200

    logout_resp = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout_resp.status_code == 200


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
