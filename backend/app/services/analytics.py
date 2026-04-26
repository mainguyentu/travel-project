from __future__ import annotations

from sqlalchemy.orm import Session

from app.clients.internal_http import internal_request_json
from app.core.config import settings
from app.repositories.analytics import AnalyticsRepository
from app.utils.serializers import destination_to_dict


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def _fetch_destination_map(self, destination_ids: list[int]) -> dict[int, dict]:
        if not destination_ids:
            return {}

        if settings.service_profile == "monolith":
            from app.repositories.destinations import DestinationRepository

            items = DestinationRepository(self.db).get_by_ids(destination_ids)
            return {int(item.id): destination_to_dict(item) for item in items}

        payload = internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/destinations/batch",
            json={"ids": destination_ids},
        )
        items = payload.get("data", [])
        mapping: dict[int, dict] = {}
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("id") is not None:
                    mapping[int(item["id"])] = item
        return mapping

    def top_favorites(self, limit: int = 10):
        rows = self.repo.top_favorites(limit * 3)
        ids = [int(destination_id) for destination_id, _ in rows]
        destination_map = self._fetch_destination_map(ids)
        result = []
        for destination_id, favorite_count in rows:
            data = destination_map.get(int(destination_id))
            if not data or data.get("status") != "active":
                continue
            data = dict(data)
            data["favorite_count"] = int(favorite_count or 0)
            result.append(data)
            if len(result) >= limit:
                break
        return result

    def top_views(self, limit: int = 10):
        rows = self.repo.top_views(limit * 3)
        ids = [int(destination_id) for destination_id, _ in rows]
        destination_map = self._fetch_destination_map(ids)
        result = []
        for destination_id, view_count in rows:
            data = destination_map.get(int(destination_id))
            if not data or data.get("status") != "active":
                continue
            data = dict(data)
            data["view_count_analytics"] = int(view_count or 0)
            result.append(data)
            if len(result) >= limit:
                break
        return result

    def top_ratings(self, limit: int = 10):
        rows = self.repo.top_ratings(limit * 3)
        ids = [int(destination_id) for destination_id, _, _ in rows]
        destination_map = self._fetch_destination_map(ids)
        result = []
        for destination_id, rating_avg, rating_count in rows:
            data = destination_map.get(int(destination_id))
            if not data or data.get("status") != "active":
                continue
            data = dict(data)
            data["rating_avg_analytics"] = round(float(rating_avg or 0), 2)
            data["rating_count"] = int(rating_count or 0)
            result.append(data)
            if len(result) >= limit:
                break
        return result

    def summary(self):
        raw = self.repo.summary()
        rating_total = raw["rating_total"]
        rating_sum_total = raw["rating_sum_total"]
        avg = (rating_sum_total / rating_total) if rating_total > 0 else 0.0
        return {
            "favorite_total": raw["favorite_total"],
            "view_total": raw["view_total"],
            "rating_total": rating_total,
            "rating_avg": round(avg, 2),
        }
