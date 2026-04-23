from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.activities import ActivityRepository, DestinationActivityRepository
from app.utils.serializers import destination_to_dict


class ActivityRecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
        self.activities = ActivityRepository(db)
        self.mappings = DestinationActivityRepository(db)

    @staticmethod
    def _to_float(value: object, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, Decimal):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _normalize_score(score: float) -> float:
        return max(0.0, min(score / 100.0, 1.0))

    @staticmethod
    def _matches_budget(feature_budget: str | None, destination_budget: str | None, requested_budget: str | None) -> bool:
        if not requested_budget:
            return True
        return requested_budget == (feature_budget or destination_budget)

    def _score_candidate(self, rule, mapping, destination, insight, feature, budget_level: str | None):
        if not insight or not getattr(insight, "final_data", None):
            return None

        if not self._matches_budget(getattr(feature, "budget_level", None), getattr(destination, "price_level", None), budget_level):
            return None

        snapshot = insight.final_data or {}
        scenery = self._to_float(snapshot.get("scenery"), 0.0)
        accessibility = self._to_float(snapshot.get("accessibility"), 0.0)
        crowd = self._to_float(snapshot.get("crowd"), 0.0)
        value = self._to_float(snapshot.get("value"), 0.0)

        scenery_weight = self._to_float(rule.scenery_weight, 0.25)
        accessibility_weight = self._to_float(rule.accessibility_weight, 0.25)
        crowd_weight = self._to_float(rule.crowd_weight, 0.25)
        value_weight = self._to_float(rule.value_weight, 0.25)
        activity_weight = self._to_float(mapping.weight, 1.0)

        crowd_factor = crowd if rule.crowd_mode == "prefer_high" else 100.0 - crowd
        base_score = (
            (scenery * scenery_weight)
            + (accessibility * accessibility_weight)
            + (crowd_factor * crowd_weight)
            + (value * value_weight)
        )
        final_score = base_score * activity_weight
        threshold = self._to_float(rule.min_match_threshold, 0.0)
        if self._normalize_score(final_score) < threshold:
            return None

        data = destination_to_dict(destination)
        data["base_score"] = round(base_score, 2)
        data["final_score"] = round(final_score, 2)
        data["activity_match_weight"] = round(activity_weight, 3)
        return data

    def recommend(self, activity_slug: str, *, page: int = 1, limit: int = 10, budget_level: str | None = None) -> dict:
        activity = self.activities.get_by_slug(activity_slug)
        if not activity:
            return {
                "activity": None,
                "highlight_destinations": [],
                "recommended_destinations": [],
                "trending": [],
            }

        rule = self.activities.get_rule(int(activity.id))
        if not rule:
            return {
                "activity": {
                    "id": activity.id,
                    "slug": activity.slug,
                    "name": activity.name,
                    "description": activity.description,
                },
                "highlight_destinations": [],
                "recommended_destinations": [],
                "trending": [],
            }

        candidate_count = self.mappings.count_candidates(int(activity.id))
        rows = self.mappings.list_candidates(int(activity.id), offset=0, limit=max(candidate_count, 0))

        scored: list[dict] = []
        trending_candidates: list[dict] = []
        for mapping, destination, insight, feature in rows:
            if self._matches_budget(getattr(feature, "budget_level", None), getattr(destination, "price_level", None), budget_level):
                trending_candidates.append(destination_to_dict(destination))
            scored_item = self._score_candidate(rule, mapping, destination, insight, feature, budget_level)
            if scored_item is not None:
                scored.append(scored_item)

        scored.sort(key=lambda item: (-item["final_score"], item["id"]))

        highlight = scored[:1]
        recommended_start = max(page - 1, 0) * limit
        recommended = scored[1 + recommended_start : 1 + recommended_start + limit]

        trending_candidates = sorted(trending_candidates, key=lambda item: (-item.get("view_count", 0), item["id"]))
        trending = trending_candidates[:limit]

        return {
            "activity": {
                "id": activity.id,
                "slug": activity.slug,
                "name": activity.name,
                "description": activity.description,
            },
            "highlight_destinations": highlight,
            "recommended_destinations": recommended,
            "trending": trending,
        }