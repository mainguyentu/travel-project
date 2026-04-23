from decimal import Decimal

from app.db.models import Activity, ActivityRule, Destination, DestinationActivity, DestinationInsight
from app.db.session import SessionLocal
from app.services.activity_recommendation import ActivityRecommendationEngine


def test_recommendation_engine_ranks_and_filters_candidates():
    db = SessionLocal()
    try:
        activity = Activity(slug="city-tour", name="City tour", description="Explore the city", is_active=True)
        db.add(activity)
        db.flush()

        db.add(
            ActivityRule(
                activity_id=activity.id,
                scenery_weight=Decimal("0.35"),
                accessibility_weight=Decimal("0.20"),
                crowd_weight=Decimal("0.20"),
                value_weight=Decimal("0.25"),
                crowd_mode="prefer_low",
                min_match_threshold=Decimal("0.30"),
            )
        )

        destinations = [
            Destination(
                name="Sky View",
                slug="sky-view",
                address="A",
                description="Best skyline and easy access",
                price_level="medium",
                open_hour="All day",
                status="active",
                rating_avg=4.5,
                view_count=120,
            ),
            Destination(
                name="City Cafe Walk",
                slug="city-cafe-walk",
                address="B",
                description="Walkable cafe and city experience",
                price_level="low",
                open_hour="All day",
                status="active",
                rating_avg=4.1,
                view_count=80,
            ),
            Destination(
                name="Hidden Village",
                slug="hidden-village",
                address="C",
                description="Remote and quiet",
                price_level="low",
                open_hour="All day",
                status="active",
                rating_avg=3.9,
                view_count=10,
            ),
        ]
        db.add_all(destinations)
        db.flush()

        db.add_all(
            [
                DestinationInsight(
                    destination_id=destinations[0].id,
                    final_data={"scenery": 90, "accessibility": 80, "crowd": 70, "value": 60},
                    score_snapshot={"scenery": 90, "accessibility": 80, "crowd": 70, "value": 60},
                ),
                DestinationInsight(
                    destination_id=destinations[1].id,
                    final_data={"scenery": 60, "accessibility": 70, "crowd": 50, "value": 75},
                    score_snapshot={"scenery": 60, "accessibility": 70, "crowd": 50, "value": 75},
                ),
                DestinationInsight(
                    destination_id=destinations[2].id,
                    final_data={"scenery": 10, "accessibility": 10, "crowd": 10, "value": 10},
                    score_snapshot={"scenery": 10, "accessibility": 10, "crowd": 10, "value": 10},
                ),
            ]
        )

        db.add_all(
            [
                DestinationActivity(destination_id=destinations[0].id, activity_id=activity.id, weight=Decimal("1.0"), source="seed"),
                DestinationActivity(destination_id=destinations[1].id, activity_id=activity.id, weight=Decimal("0.8"), source="seed"),
                DestinationActivity(destination_id=destinations[2].id, activity_id=activity.id, weight=Decimal("0.6"), source="seed"),
            ]
        )
        db.commit()

        engine = ActivityRecommendationEngine(db)
        result = engine.recommend("city-tour", page=1, limit=10)

        assert result["activity"]["slug"] == "city-tour"
        assert [item["slug"] for item in result["highlight_destinations"]] == ["sky-view"]
        assert [item["slug"] for item in result["recommended_destinations"]] == ["city-cafe-walk"]
        assert [item["slug"] for item in result["trending"]] == ["sky-view", "city-cafe-walk", "hidden-village"]
    finally:
        db.close()


def test_recommendation_engine_prefers_high_crowd_when_configured():
    db = SessionLocal()
    try:
        activity = Activity(slug="food-tour", name="Food tour", description="Explore food", is_active=True)
        db.add(activity)
        db.flush()

        db.add(
            ActivityRule(
                activity_id=activity.id,
                scenery_weight=Decimal("0.20"),
                accessibility_weight=Decimal("0.20"),
                crowd_weight=Decimal("0.35"),
                value_weight=Decimal("0.25"),
                crowd_mode="prefer_high",
                min_match_threshold=Decimal("0.10"),
            )
        )

        high_crowd = Destination(
            name="Busy Food Street",
            slug="busy-food-street",
            address="A",
            description="Street food and market",
            price_level="low",
            open_hour="All day",
            status="active",
            rating_avg=4.2,
            view_count=150,
        )
        low_crowd = Destination(
            name="Quiet Food Corner",
            slug="quiet-food-corner",
            address="B",
            description="Small local food place",
            price_level="low",
            open_hour="All day",
            status="active",
            rating_avg=4.4,
            view_count=50,
        )
        db.add_all([high_crowd, low_crowd])
        db.flush()

        db.add_all(
            [
                DestinationInsight(
                    destination_id=high_crowd.id,
                    final_data={"scenery": 35, "accessibility": 60, "crowd": 90, "value": 70},
                    score_snapshot={"scenery": 35, "accessibility": 60, "crowd": 90, "value": 70},
                ),
                DestinationInsight(
                    destination_id=low_crowd.id,
                    final_data={"scenery": 45, "accessibility": 60, "crowd": 20, "value": 70},
                    score_snapshot={"scenery": 45, "accessibility": 60, "crowd": 20, "value": 70},
                ),
            ]
        )

        db.add_all(
            [
                DestinationActivity(destination_id=high_crowd.id, activity_id=activity.id, weight=Decimal("1.0"), source="seed"),
                DestinationActivity(destination_id=low_crowd.id, activity_id=activity.id, weight=Decimal("1.0"), source="seed"),
            ]
        )
        db.commit()

        engine = ActivityRecommendationEngine(db)
        result = engine.recommend("food-tour", page=1, limit=10)

        assert [item["slug"] for item in result["highlight_destinations"]] == ["busy-food-street"]
        assert [item["slug"] for item in result["recommended_destinations"]] == ["quiet-food-corner"]
    finally:
        db.close()