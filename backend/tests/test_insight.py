from app.db.session import SessionLocal
from app.db.models import Destination, DestinationInsight
from app.services.insight import InsightService, BASELINE_SCORE


def _create_destination(db, slug: str):
    destination = Destination(
        name=f"Dest {slug}",
        slug=slug,
        price_level="medium",
        status="active",
    )
    db.add(destination)
    db.flush()
    return destination


def test_insight_initialize_baseline():
    db = SessionLocal()
    try:
        destination = _create_destination(db, "insight-baseline")
        insight = InsightService(db).initialize_for_destination(destination.id)
        db.commit()

        assert insight.score_snapshot["scenery"] == BASELINE_SCORE
        assert insight.score_snapshot["accessibility"] == BASELINE_SCORE
        assert insight.score_snapshot["crowd"] == BASELINE_SCORE
        assert insight.score_snapshot["value"] == BASELINE_SCORE

        assert insight.human_override == {
            "scenery_level": "medium",
            "accessibility_level": "medium",
            "crowd_level": "medium",
            "value_level": "medium",
        }

        assert insight.final_data["score"] == BASELINE_SCORE
        assert insight.final_data["status"] == "insufficient_data"

        cache = insight.insight_cache
        assert cache["total_reviews"] == 0
        assert cache["sum_weight_scenery"] == 0.0
        assert cache["sum_weight_accessibility"] == 0.0
        assert cache["sum_weight_crowd"] == 0.0
        assert cache["sum_weight_value"] == 0.0
    finally:
        db.close()


def test_insight_apply_rating_updates_cache_and_scores():
    db = SessionLocal()
    try:
        destination = _create_destination(db, "insight-rating")
        InsightService(db).initialize_for_destination(destination.id)

        service = InsightService(db)
        service.apply_rating_update(
            destination_id=destination.id,
            new_score=5,
            new_comment="Rất đẹp và dễ đi",
            old_score=None,
            old_comment=None,
            is_new_rating=True,
        )
        db.commit()

        insight = db.get(DestinationInsight, destination.id)
        cache = insight.insight_cache

        assert cache["total_reviews"] == 1
        assert cache["sum_weight_scenery"] > 0
        assert cache["sum_weight_accessibility"] > 0
        assert cache["sum_weight_crowd"] == 0.0
        assert cache["sum_weight_value"] == 0.0

        assert insight.score_snapshot["scenery"] > BASELINE_SCORE
        assert insight.score_snapshot["accessibility"] > BASELINE_SCORE
        assert insight.score_snapshot["crowd"] == BASELINE_SCORE
        assert insight.score_snapshot["value"] == BASELINE_SCORE

        service.apply_rating_update(
            destination_id=destination.id,
            new_score=1,
            new_comment="Không đông nhưng giá đắt",
            old_score=5,
            old_comment="Rất đẹp và dễ đi",
            is_new_rating=False,
        )
        db.commit()

        insight = db.get(DestinationInsight, destination.id)
        cache = insight.insight_cache

        assert cache["total_reviews"] == 1
        assert cache["sum_weight_scenery"] == 0.0
        assert cache["sum_weight_accessibility"] == 0.0
        assert cache["sum_weight_crowd"] > 0
        assert cache["sum_weight_value"] > 0

        assert insight.score_snapshot["scenery"] == BASELINE_SCORE
        assert insight.score_snapshot["accessibility"] == BASELINE_SCORE
        assert insight.score_snapshot["crowd"] < BASELINE_SCORE
        assert insight.score_snapshot["value"] < BASELINE_SCORE
    finally:
        db.close()


def test_insight_short_review_reduced_weight():
    db = SessionLocal()
    try:
        destination = _create_destination(db, "insight-short")
        InsightService(db).initialize_for_destination(destination.id)

        InsightService(db).apply_rating_update(
            destination_id=destination.id,
            new_score=5,
            new_comment="đẹp",
            old_score=None,
            old_comment=None,
            is_new_rating=True,
        )
        db.commit()

        insight = db.get(DestinationInsight, destination.id)
        assert insight.insight_cache["sum_weight_scenery"] > 0
        assert insight.score_snapshot["scenery"] == 30.0
        assert insight.insight_cache["total_reviews"] == 1
    finally:
        db.close()


def test_insight_reject_ad_spam():
    db = SessionLocal()
    try:
        destination = _create_destination(db, "insight-spam")
        InsightService(db).initialize_for_destination(destination.id)

        InsightService(db).apply_rating_update(
            destination_id=destination.id,
            new_score=5,
            new_comment="đẹp nhưng liên hệ zalo 0901234567",
            old_score=None,
            old_comment=None,
            is_new_rating=True,
        )
        db.commit()

        insight = db.get(DestinationInsight, destination.id)
        assert insight.insight_cache["sum_weight_scenery"] == 0.0
        assert insight.insight_cache["total_reviews"] == 1
    finally:
        db.close()
