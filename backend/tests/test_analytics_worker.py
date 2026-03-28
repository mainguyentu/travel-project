from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.db.models import Category, CategoryDestination, Destination
from app.db.session import SessionLocal
from app.worker.handlers import dispatch_event

client = TestClient(app)


def _seed_destination() -> int:
    suffix = uuid4().hex[:8]
    db = SessionLocal()
    try:
        category = Category(name=f"Analytics {suffix}", slug=f"analytics-{suffix}", descriptions="analytics")
        db.add(category)
        db.flush()

        destination = Destination(
            name=f"Analytics Place {suffix}",
            slug=f"analytics-place-{suffix}",
            address="Da Nang",
            description="Destination for analytics tests",
            price_level="medium",
            open_hour="All day",
            status="active",
            rating_avg=0,
            view_count=0,
        )
        db.add(destination)
        db.flush()
        db.add(CategoryDestination(category_id=category.id, destination_id=destination.id))
        db.commit()
        return int(destination.id)
    finally:
        db.close()


def test_worker_handlers_update_analytics_metrics():
    destination_id = _seed_destination()

    dispatch_event(
        {
            "event_type": "favorite.created",
            "payload": {"destination_id": destination_id, "delta": 1},
        }
    )
    dispatch_event(
        {
            "event_type": "rating.upserted",
            "payload": {"destination_id": destination_id, "old_score": None, "new_score": 4},
        }
    )
    dispatch_event(
        {
            "event_type": "destination.viewed",
            "payload": {"destination_id": destination_id, "delta": 3},
        }
    )

    resp = client.get("/api/v1/analytics/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["favorite_total"] >= 1
    assert data["rating_total"] >= 1
    assert data["view_total"] >= 3


def test_analytics_top_endpoints_return_lists():
    _seed_destination()

    for path in (
        "/api/v1/analytics/top-favorites",
        "/api/v1/analytics/top-ratings",
        "/api/v1/analytics/top-views",
    ):
        resp = client.get(path)
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)
