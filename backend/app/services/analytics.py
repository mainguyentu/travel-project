from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.analytics import AnalyticsRepository
from app.utils.serializers import destination_to_dict


class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def top_favorites(self, limit: int = 10):
        rows = self.repo.top_favorites(limit)
        result = []
        for destination, favorite_count in rows:
            data = destination_to_dict(destination)
            data["favorite_count"] = int(favorite_count or 0)
            result.append(data)
        return result

    def top_views(self, limit: int = 10):
        rows = self.repo.top_views(limit)
        result = []
        for destination, view_count in rows:
            data = destination_to_dict(destination)
            data["view_count_analytics"] = int(view_count or 0)
            result.append(data)
        return result

    def top_ratings(self, limit: int = 10):
        rows = self.repo.top_ratings(limit)
        result = []
        for destination, rating_avg, rating_count in rows:
            data = destination_to_dict(destination)
            data["rating_avg_analytics"] = round(float(rating_avg or 0), 2)
            data["rating_count"] = int(rating_count or 0)
            result.append(data)
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
