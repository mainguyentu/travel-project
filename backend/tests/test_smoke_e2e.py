import os
from uuid import uuid4

import httpx
import pytest

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8080").rstrip("/")
TIMEOUT = float(os.getenv("E2E_TIMEOUT_SECONDS", "10"))


@pytest.fixture(scope="session")
def e2e_client() -> httpx.Client:
    try:
        with httpx.Client(base_url=BASE_URL, timeout=TIMEOUT) as client:
            health = client.get("/health")
            if health.status_code >= 500:
                pytest.skip(f"E2E target unhealthy: {BASE_URL}")
            yield client
    except Exception as exc:  # pragma: no cover - environment-dependent
        pytest.skip(f"E2E target unavailable: {BASE_URL} ({exc})")


def test_compose_smoke_end_to_end(e2e_client: httpx.Client):
    suffix = uuid4().hex[:8]
    user_email = f"smoke-{suffix}@alats.vn"
    user_password = "User@123"

    # Register + login normal user.
    register_resp = e2e_client.post(
        "/api/v1/auth/register",
        json={"name": "Smoke User", "email": user_email, "password": user_password},
    )
    assert register_resp.status_code in (200, 201, 409)

    login_user = e2e_client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "password": user_password},
    )
    assert login_user.status_code == 200
    assert login_user.json().get("success") is True
    user_access = login_user.json()["data"]["access_token"]

    # Login admin seeded account and create category + destination.
    login_admin = e2e_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@alats.vn", "password": "Admin@123"},
    )
    assert login_admin.status_code == 200
    admin_access = login_admin.json()["data"]["access_token"]

    category_slug = f"smoke-cat-{suffix}"
    category_resp = e2e_client.post(
        "/api/v1/admin/categories",
        headers={"Authorization": f"Bearer {admin_access}"},
        json={"name": f"Smoke Category {suffix}", "slug": category_slug, "descriptions": "Smoke test"},
    )
    assert category_resp.status_code in (200, 201, 409)

    categories_resp = e2e_client.get(
        "/api/v1/admin/categories",
        headers={"Authorization": f"Bearer {admin_access}"},
    )
    assert categories_resp.status_code == 200
    category_id = next(
        c["id"]
        for c in categories_resp.json()["data"]
        if c.get("slug") == category_slug
    )

    destination_slug = f"smoke-destination-{suffix}"
    destination_resp = e2e_client.post(
        "/api/v1/admin/destinations",
        headers={"Authorization": f"Bearer {admin_access}"},
        json={
            "name": f"Smoke Destination {suffix}",
            "slug": destination_slug,
            "address": "Da Nang",
            "description": "Smoke destination",
            "price_level": "medium",
            "open_hour": "All day",
            "img_url": "https://example.com/smoke.jpg",
            "url_map": "https://maps.google.com",
            "lat": 16.047079,
            "lng": 108.20623,
            "status": "active",
            "category_ids": [category_id],
        },
    )
    assert destination_resp.status_code in (200, 201)
    destination_id = destination_resp.json()["data"]["id"]

    # User journey: view + favorite + rate.
    detail_resp = e2e_client.get(f"/api/v1/destinations/{destination_id}")
    assert detail_resp.status_code == 200

    favorite_resp = e2e_client.post(
        f"/api/v1/me/favorites/{destination_id}",
        headers={"Authorization": f"Bearer {user_access}"},
    )
    assert favorite_resp.status_code == 200

    rating_resp = e2e_client.put(
        f"/api/v1/me/ratings/{destination_id}",
        headers={"Authorization": f"Bearer {user_access}"},
        json={"rating_score": 5, "comment": "Great smoke test"},
    )
    assert rating_resp.status_code == 200

    analytics_resp = e2e_client.get("/api/v1/analytics/summary")
    assert analytics_resp.status_code == 200
    assert analytics_resp.json().get("success") is True
