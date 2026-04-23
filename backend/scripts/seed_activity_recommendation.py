import sys
import unicodedata
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.models import (  # noqa: E402
    Activity,
    ActivityRule,
    Destination,
    DestinationActivity,
    DestinationFeature,
)
from app.db.session import SessionLocal  # noqa: E402


ACTIVITY_SPECS = [
    {
        "slug": "chill-bien",
        "name": "Chill bien",
        "description": "Nghi duong, thu gian o bo bien, resort va quan cafe view bien.",
        "rules": {
            "scenery_weight": Decimal("0.35"),
            "accessibility_weight": Decimal("0.20"),
            "crowd_weight": Decimal("0.20"),
            "value_weight": Decimal("0.25"),
            "crowd_mode": "prefer_low",
            "min_match_threshold": Decimal("0.60"),
        },
        "keywords": {
            "beach",
            "bien",
            "resort",
            "coastal",
            "shore",
            "cafe bien",
            "seaside",
            "my khe",
        },
    },
    {
        "slug": "kham-pha-thien-nhien",
        "name": "Kham pha thien nhien",
        "description": "Trai nghiem nui, rung, thac va cac hoat dong ngoai troi.",
        "rules": {
            "scenery_weight": Decimal("0.35"),
            "accessibility_weight": Decimal("0.15"),
            "crowd_weight": Decimal("0.15"),
            "value_weight": Decimal("0.35"),
            "crowd_mode": "prefer_low",
            "min_match_threshold": Decimal("0.55"),
        },
        "keywords": {
            "nature",
            "thien nhien",
            "nui",
            "rung",
            "thac",
            "waterfall",
            "trek",
            "hiking",
            "park",
            "forest",
        },
    },
    {
        "slug": "city-tour",
        "name": "City tour",
        "description": "Kham pha cac diem noi bat khu trung tam va do thi.",
        "rules": {
            "scenery_weight": Decimal("0.25"),
            "accessibility_weight": Decimal("0.30"),
            "crowd_weight": Decimal("0.20"),
            "value_weight": Decimal("0.25"),
            "crowd_mode": "prefer_high",
            "min_match_threshold": Decimal("0.50"),
        },
        "keywords": {
            "city",
            "landmark",
            "downtown",
            "trung tam",
            "pho",
            "cau",
            "bridge",
            "cho",
            "market",
        },
    },
    {
        "slug": "food-tour",
        "name": "Food tour",
        "description": "Trai nghiem am thuc dia phuong, quan an va cho street food.",
        "rules": {
            "scenery_weight": Decimal("0.20"),
            "accessibility_weight": Decimal("0.20"),
            "crowd_weight": Decimal("0.25"),
            "value_weight": Decimal("0.35"),
            "crowd_mode": "prefer_high",
            "min_match_threshold": Decimal("0.55"),
        },
        "keywords": {
            "food",
            "am thuc",
            "quan an",
            "restaurant",
            "street food",
            "cho",
            "market",
            "local food",
            "mon an",
        },
    },
    {
        "slug": "van-hoa-lich-su",
        "name": "Van hoa lich su",
        "description": "Tham quan di tich, bao tang va diem den van hoa.",
        "rules": {
            "scenery_weight": Decimal("0.20"),
            "accessibility_weight": Decimal("0.30"),
            "crowd_weight": Decimal("0.20"),
            "value_weight": Decimal("0.30"),
            "crowd_mode": "prefer_low",
            "min_match_threshold": Decimal("0.55"),
        },
        "keywords": {
            "culture",
            "van hoa",
            "history",
            "lich su",
            "bao tang",
            "museum",
            "di tich",
            "chua",
            "temple",
            "pagoda",
        },
    },
]

OUTDOOR_HINTS = {"beach", "bien", "park", "nature", "nui", "rung", "waterfall", "thac", "bridge", "cau"}
INDOOR_HINTS = {"museum", "bao tang", "indoor", "gallery", "art", "chua", "temple"}


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    nfkd = unicodedata.normalize("NFKD", value)
    no_accents = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return no_accents.lower().strip()


def _build_destination_text(destination: Destination) -> str:
    category_tokens: list[str] = []
    for rel in destination.categories:
        category = rel.category
        if category:
            category_tokens.append(_normalize_text(category.name))
            category_tokens.append(_normalize_text(category.slug))
    chunks = [
        _normalize_text(destination.name),
        _normalize_text(destination.description),
        _normalize_text(destination.address),
        " ".join(category_tokens),
    ]
    return " ".join(chunk for chunk in chunks if chunk)


def _score_destination_for_activity(destination_text: str, keywords: set[str]) -> int:
    return sum(1 for keyword in keywords if keyword in destination_text)


def _weight_from_matches(matches: int) -> Decimal:
    if matches >= 4:
        return Decimal("1.000")
    if matches == 3:
        return Decimal("0.900")
    if matches == 2:
        return Decimal("0.800")
    if matches == 1:
        return Decimal("0.650")
    return Decimal("0")


def _upsert_activities_and_rules(db):
    activities_by_slug: dict[str, Activity] = {}

    for spec in ACTIVITY_SPECS:
        activity = db.query(Activity).filter(Activity.slug == spec["slug"]).first()
        if not activity:
            activity = Activity(slug=spec["slug"])
            db.add(activity)

        activity.name = spec["name"]
        activity.description = spec["description"]
        activity.is_active = True
        db.flush()
        activities_by_slug[spec["slug"]] = activity

        rule = db.query(ActivityRule).filter(ActivityRule.activity_id == activity.id).first()
        if not rule:
            rule = ActivityRule(activity_id=activity.id)
            db.add(rule)

        rule_data = spec["rules"]
        rule.scenery_weight = rule_data["scenery_weight"]
        rule.accessibility_weight = rule_data["accessibility_weight"]
        rule.crowd_weight = rule_data["crowd_weight"]
        rule.value_weight = rule_data["value_weight"]
        rule.crowd_mode = rule_data["crowd_mode"]
        rule.min_match_threshold = rule_data["min_match_threshold"]

    db.flush()
    return activities_by_slug


def _upsert_destination_features(db, destination: Destination, destination_text: str):
    features = db.query(DestinationFeature).filter(DestinationFeature.destination_id == destination.id).first()
    if not features:
        features = DestinationFeature(destination_id=destination.id)
        db.add(features)

    outdoor_hits = any(keyword in destination_text for keyword in OUTDOOR_HINTS)
    indoor_hits = any(keyword in destination_text for keyword in INDOOR_HINTS)

    features.is_outdoor = outdoor_hits if outdoor_hits else None
    features.is_indoor = indoor_hits if indoor_hits else None
    features.suitable_time = "both"
    features.budget_level = destination.price_level or "medium"
    features.duration_suggested_minutes = 180 if outdoor_hits else 120


def _upsert_destination_activity_mappings(db, activities_by_slug: dict[str, Activity]):
    destinations = db.query(Destination).all()
    created_or_updated = 0

    for destination in destinations:
        destination_text = _build_destination_text(destination)
        _upsert_destination_features(db, destination, destination_text)

        for spec in ACTIVITY_SPECS:
            matches = _score_destination_for_activity(destination_text, spec["keywords"])
            weight = _weight_from_matches(matches)
            if weight <= 0:
                continue

            activity = activities_by_slug[spec["slug"]]
            mapping = (
                db.query(DestinationActivity)
                .filter(
                    DestinationActivity.destination_id == destination.id,
                    DestinationActivity.activity_id == activity.id,
                )
                .first()
            )
            if not mapping:
                mapping = DestinationActivity(
                    destination_id=destination.id,
                    activity_id=activity.id,
                    source="seed",
                )
                db.add(mapping)

            mapping.weight = weight
            mapping.source = "seed"
            created_or_updated += 1

    db.flush()
    return len(destinations), created_or_updated


def run():
    db = SessionLocal()
    try:
        activities_by_slug = _upsert_activities_and_rules(db)
        destination_count, mapping_count = _upsert_destination_activity_mappings(db, activities_by_slug)
        db.commit()

        print("Activity recommendation seed done")
        print(f"Activities upserted: {len(activities_by_slug)}")
        print(f"Destinations processed: {destination_count}")
        print(f"Destination-activity mappings upserted: {mapping_count}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
