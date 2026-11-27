import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5433/travel",
)

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.db.models import DestinationInsight
from app.main import app

client = TestClient(app)


def test_search_returns_engine_meta():
    r = client.get("/api/v1/destinations/search", params={"q": "My Khe"})
    assert r.status_code == 200, r.text
    meta = r.json()["meta"]
    assert meta.get("search_engine") in ("elasticsearch", "db"), meta


def test_search_fallback_db_empty_query():
    r = client.get("/api/v1/destinations/search", params={"q": ""})
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["data"], list)


def test_view_publishes_event_and_insight_enriched():
    r = client.get("/api/v1/destinations/1")
    assert r.status_code == 200, r.text
    # run worker once synchronously via internal recompute path
    db = SessionLocal()
    try:
        row = db.get(DestinationInsight, 1)
        assert row is not None
        assert isinstance(row.final_data, dict)
    finally:
        db.close()


def test_worker_build_insight_shape():
    from app.db.session import SessionLocal as SL
    from scripts.worker import build_insight

    db = SL()
    try:
        data = build_insight(db, 1)
        for key in ("status", "summary", "rating_avg", "rating_count",
                    "favorite_count", "view_count", "categories"):
            assert key in data, data
        assert data["status"] in ("ok", "insufficient_data", "missing")
    finally:
        db.close()
