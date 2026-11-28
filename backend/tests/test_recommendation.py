import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.db.models import Favorite, User, UserToken, UserView
from app.db.session import SessionLocal
from app.main import app

client = TestClient(app)

EMAIL = "tdd-reco@example.com"


def _auth_headers() -> dict:
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=EMAIL).first()
        if user:
            db.query(Favorite).filter_by(user_id=user.id).delete()
            db.query(UserView).filter_by(user_id=user.id).delete()
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


def test_recommendations_require_auth():
    r = client.get("/api/v1/me/recommendations")
    assert r.status_code == 401
    r = client.get("/api/v1/me/itinerary")
    assert r.status_code == 401


def test_new_user_gets_fallback_and_itinerary():
    h = _auth_headers()
    r = client.get("/api/v1/me/recommendations?limit=5", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    assert body["profile"]["is_new"] is True
    assert isinstance(body["matched"], list) and isinstance(body["explore"], list)
    assert body["matched"], "user mới phải có fallback hot toàn site"

    it = client.get("/api/v1/me/itinerary?limit=3", headers=h)
    assert it.status_code == 200, it.text
    data = it.json()["data"]
    assert len(data["itinerary"]) == 3
    assert [s["order"] for s in data["itinerary"]] == [1, 2, 3]
    assert all(s["slot"] for s in data["itinerary"])
    assert data["total_match"] >= 0


def test_favorite_drives_matched_and_view_tracked():
    h = _auth_headers()
    # ♥ Bãi biển Mỹ Khê (id 1, category bien)
    r = client.post("/api/v1/me/favorites/1", headers=h)
    assert r.status_code == 200, r.text
    # Xem detail Hội An (id 3) với token -> ghi user_views
    d = client.get("/api/v1/destinations/3", headers=h)
    assert d.status_code == 200, d.text

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=EMAIL).first()
        assert db.query(UserView).filter_by(user_id=user.id, destination_id=3).first() is not None
    finally:
        db.close()

    r = client.get("/api/v1/me/recommendations?limit=10", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    assert body["profile"]["is_new"] is False
    assert body["profile"]["preferred_price"] in ("free", "low", "medium", "high", None)
    matched_ids = [s["destination"]["id"] for s in body["matched"]]
    # Des đã ♥ (id 1) phải bị loại khỏi đề xuất
    assert 1 not in matched_ids
    for s in body["matched"]:
        assert s["match"] >= 60.0
        assert s["reasons"]
        assert set(s["components"].keys()) == {"category", "quality", "popularity", "price"}

    # Itinerary không lặp category liên tiếp khi còn lựa chọn
    it = client.get("/api/v1/me/itinerary?limit=3", headers=h)
    assert it.status_code == 200, it.text
    items = it.json()["data"]["itinerary"]
    assert isinstance(items, list)


def test_admin_bulk_external_rating():
    import time
    admin = client.post("/api/v1/auth/login", json={"email": "admin@alats.vn", "password": "Admin@123"})
    assert admin.status_code == 200, admin.text
    ah = {"Authorization": f"Bearer {admin.json()['data']['access_token']}"}
    slug = f"ext-place-{int(time.time())}"
    r = client.post(
        "/api/v1/admin/destinations/bulk",
        json={"items": [{
            "name": "Ext Place", "slug": slug,
            "external_rating_avg": 4.6, "external_rating_count": 12345,
            "external_source": "google_maps",
        }]},
        headers=ah,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"][0]
    assert data["external_rating_avg"] == 4.6
    assert data["external_rating_count"] == 12345
    assert data["external_source"] == "google_maps"
