import time
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db.models import Category, CategoryDestination, Destination
from app.db.session import SessionLocal
from app import app_factory
from app.core.config import settings
from app.routers import destinations as destinations_router

client = TestClient(app)


class _FakePipeline:
    def __init__(self, counters: dict[str, int]):
        self._counters = counters
        self._results: list[int | bool] = []

    def incr(self, key: str, amount: int = 1):
        self._counters[key] = self._counters.get(key, 0) + amount
        self._results.append(self._counters[key])
        return self

    def expire(self, key: str, ttl: int):
        _ = (key, ttl)
        self._results.append(True)
        return self

    def execute(self):
        return self._results


class _FakeRedis:
    def __init__(self):
        self._counters: dict[str, int] = {}

    def pipeline(self):
        return _FakePipeline(self._counters)


def _seed_destinations() -> tuple[str, int, int, str, str]:
    suffix = uuid4().hex[:8]
    category_slug = f"beach-{suffix}"

    db = SessionLocal()
    try:
        category = Category(name=f"Beach {suffix}", slug=category_slug, descriptions="Beach category")
        db.add(category)
        db.flush()

        d1 = Destination(
            name=f"Sunny Beach {suffix}",
            slug=f"sunny-beach-{suffix}",
            address="A",
            description="A sunny place for beach lovers",
            price_level="free",
            open_hour="All day",
            status="active",
            rating_avg=4.8,
            view_count=120,
        )
        d2 = Destination(
            name=f"Luxury Coast {suffix}",
            slug=f"luxury-coast-{suffix}",
            address="B",
            description="Premium beach experience",
            price_level="high",
            open_hour="All day",
            status="active",
            rating_avg=3.2,
            view_count=50,
        )
        d3 = Destination(
            name=f"Forest Trail {suffix}",
            slug=f"forest-trail-{suffix}",
            address="C",
            description="Mountain and forest route",
            price_level="free",
            open_hour="All day",
            status="active",
            rating_avg=4.1,
            view_count=80,
        )
        db.add_all([d1, d2, d3])
        db.flush()

        db.add(CategoryDestination(category_id=category.id, destination_id=d1.id))
        db.add(CategoryDestination(category_id=category.id, destination_id=d2.id))
        db.commit()

        return category_slug, int(d1.id), int(d2.id), d1.slug, d2.slug
    finally:
        db.close()


def test_rate_limit_blocks_after_threshold(monkeypatch):
    fake_redis = _FakeRedis()
    monkeypatch.setattr(app_factory, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(settings, "rate_limit_ip_per_min", 2)

    r1 = client.get("/health")
    r2 = client.get("/health")
    r3 = client.get("/health")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
    assert r3.json()["success"] is False
    assert r3.json()["error"]["code"] == "RATE_LIMIT"


def test_destinations_list_and_search_filters_work():
    category_slug, _, _, expected_slug, _ = _seed_destinations()

    list_resp = client.get(
        "/api/v1/destinations",
        params={
            "category_slug": category_slug,
            "price_level": "free",
            "rating_min": 4,
            "keyword": "sunny",
            "sort": "views",
            "page": 1,
            "limit": 20,
        },
    )
    assert list_resp.status_code == 200
    list_data = list_resp.json()["data"]
    assert len(list_data) >= 1
    assert any(item["slug"] == expected_slug for item in list_data)

    search_resp = client.get(
        "/api/v1/destinations/search",
        params={"q": "beach", "category_slug": category_slug, "page": 1, "limit": 20},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()["data"]
    assert len(search_data) >= 2
    assert search_data[0]["rating_avg"] >= search_data[1]["rating_avg"]


def test_search_uses_elasticsearch_ids_order_when_available(monkeypatch):
    category_slug, first_id, second_id, first_slug, second_slug = _seed_destinations()
    monkeypatch.setattr(settings, "search_use_elasticsearch", True)
    monkeypatch.setattr(
        destinations_router,
        "search_destination_ids",
        lambda **_: [second_id, first_id],
    )

    resp = client.get(
        "/api/v1/destinations/search",
        params={"q": "beach", "category_slug": category_slug, "page": 1, "limit": 20},
    )
    assert resp.status_code == 200
    slugs = [item["slug"] for item in resp.json()["data"]]
    assert slugs[:2] == [second_slug, first_slug]


def test_search_falls_back_to_db_when_es_unavailable(monkeypatch):
    category_slug, _, _, _, _ = _seed_destinations()
    monkeypatch.setattr(settings, "search_use_elasticsearch", True)
    monkeypatch.setattr(destinations_router, "search_destination_ids", lambda **_: None)

    resp = client.get(
        "/api/v1/destinations/search",
        params={"q": "beach", "category_slug": category_slug, "page": 1, "limit": 20},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 2


def test_destinations_sort_non_increasing_for_views_and_rating():
    _seed_destinations()

    views_resp = client.get("/api/v1/destinations", params={"sort": "views", "page": 1, "limit": 20})
    ratings_resp = client.get("/api/v1/destinations", params={"sort": "rating", "page": 1, "limit": 20})

    assert views_resp.status_code == 200
    assert ratings_resp.status_code == 200

    view_values = [item["view_count"] for item in views_resp.json()["data"]]
    rating_values = [item["rating_avg"] for item in ratings_resp.json()["data"]]

    assert view_values == sorted(view_values, reverse=True)
    assert rating_values == sorted(rating_values, reverse=True)


def test_invalid_filter_params_return_validation_error():
    invalid_page = client.get("/api/v1/destinations", params={"page": 0, "limit": 20})
    invalid_limit = client.get("/api/v1/destinations", params={"page": 1, "limit": 999})

    assert invalid_page.status_code == 400
    assert invalid_page.json()["error"]["code"] == "VALIDATION_ERROR"

    assert invalid_limit.status_code == 400
    assert invalid_limit.json()["error"]["code"] == "VALIDATION_ERROR"


def test_destinations_list_performance_baseline():
    _seed_destinations()

    durations = []
    for _ in range(5):
        start = time.perf_counter()
        resp = client.get("/api/v1/destinations", params={"page": 1, "limit": 20})
        end = time.perf_counter()

        assert resp.status_code == 200
        durations.append(end - start)

    avg_duration = sum(durations) / len(durations)
    p95_duration = max(durations)

    # This is a coarse regression guard, not a microbenchmark.
    assert avg_duration < 2.0
    assert p95_duration < 3.0
