from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.db.models import Destination, DestinationMetric


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_metric(self, destination_id: int) -> DestinationMetric:
        metric = self.db.get(DestinationMetric, destination_id)
        if metric:
            return metric
        metric = DestinationMetric(destination_id=destination_id)
        self.db.add(metric)
        self.db.flush()
        return metric

    def apply_favorite_delta(self, destination_id: int, delta: int) -> DestinationMetric:
        metric = self.ensure_metric(destination_id)
        metric.favorite_count = max(int(metric.favorite_count or 0) + delta, 0)
        self.db.flush()
        return metric

    def apply_view_delta(self, destination_id: int, delta: int = 1) -> DestinationMetric:
        metric = self.ensure_metric(destination_id)
        metric.view_count = max(int(metric.view_count or 0) + delta, 0)
        self.db.flush()
        return metric

    def apply_rating_upsert(self, destination_id: int, old_score: int | None, new_score: int) -> DestinationMetric:
        metric = self.ensure_metric(destination_id)

        if old_score is None:
            metric.rating_count = int(metric.rating_count or 0) + 1
            metric.rating_sum = int(metric.rating_sum or 0) + int(new_score)
        else:
            metric.rating_sum = int(metric.rating_sum or 0) + int(new_score) - int(old_score)

        self.db.flush()
        return metric

    def top_favorites(self, limit: int):
        stmt = (
            select(Destination, DestinationMetric.favorite_count)
            .join(DestinationMetric, DestinationMetric.destination_id == Destination.id)
            .where(Destination.status == "active")
            .order_by(DestinationMetric.favorite_count.desc(), Destination.id.asc())
            .limit(limit)
        )
        return self.db.execute(stmt).all()

    def top_views(self, limit: int):
        stmt = (
            select(Destination, DestinationMetric.view_count)
            .join(DestinationMetric, DestinationMetric.destination_id == Destination.id)
            .where(Destination.status == "active")
            .order_by(DestinationMetric.view_count.desc(), Destination.id.asc())
            .limit(limit)
        )
        return self.db.execute(stmt).all()

    def top_ratings(self, limit: int):
        avg_expr = case(
            (DestinationMetric.rating_count > 0, (DestinationMetric.rating_sum * 1.0) / DestinationMetric.rating_count),
            else_=0.0,
        )
        stmt = (
            select(Destination, avg_expr.label("rating_avg"), DestinationMetric.rating_count)
            .join(DestinationMetric, DestinationMetric.destination_id == Destination.id)
            .where(Destination.status == "active")
            .order_by(avg_expr.desc(), DestinationMetric.rating_count.desc(), Destination.id.asc())
            .limit(limit)
        )
        return self.db.execute(stmt).all()

    def summary(self):
        stmt = select(
            func.coalesce(func.sum(DestinationMetric.favorite_count), 0).label("favorite_total"),
            func.coalesce(func.sum(DestinationMetric.view_count), 0).label("view_total"),
            func.coalesce(func.sum(DestinationMetric.rating_count), 0).label("rating_total"),
            func.coalesce(func.sum(DestinationMetric.rating_sum), 0).label("rating_sum_total"),
        )
        row = self.db.execute(stmt).first()
        return {
            "favorite_total": int(row.favorite_total if row else 0),
            "view_total": int(row.view_total if row else 0),
            "rating_total": int(row.rating_total if row else 0),
            "rating_sum_total": int(row.rating_sum_total if row else 0),
        }
