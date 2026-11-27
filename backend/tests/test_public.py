import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_landing_shape():
    r = client.get("/api/v1/public/landing")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert {"highlights", "categories", "top_ratings", "top_favorites"} <= set(data)
    assert len(data["highlights"]) >= 3


def test_list_filter_pagination():
    r = client.get("/api/v1/destinations", params={"page": 1, "limit": 2})
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] >= 3
    assert len(body["data"]) == 2

    r = client.get("/api/v1/destinations", params={"category_slug": "bien"})
    slugs = [d["slug"] for d in r.json()["data"]]
    assert "bai-bien-my-khe" in slugs

    r = client.get("/api/v1/destinations", params={"price_level": "bogus"})
    assert r.status_code == 400

    r = client.get("/api/v1/destinations", params={"limit": 101})
    assert r.status_code == 400


def test_search_and_detail_view_count():
    r = client.get("/api/v1/destinations/search", params={"q": "Hội An"})
    assert r.status_code == 200
    assert any("hoi-an" in d["slug"] for d in r.json()["data"])

    first = client.get("/api/v1/destinations/1")
    assert first.status_code == 200, first.text
    v1 = first.json()["data"]["view_count"]
    second = client.get("/api/v1/destinations/1")
    v2 = second.json()["data"]["view_count"]
    assert v2 == v1 + 1
    assert "insight" in second.json()["data"]
    assert "metrics" in second.json()["data"]

    missing = client.get("/api/v1/destinations/999999")
    assert missing.status_code == 404
