from sqlalchemy.orm import Session
from sqlalchemy import select
import re
import unicodedata
from app.core.errors import AppError
from app.db.models import Category
from app.repositories.destinations import DestinationRepository
from app.repositories.categories import CategoryRepository
from app.core.cache import invalidate_destination_cache, invalidate_admin_stats_cache, invalidate_public_landing_cache
from app.services.insight import InsightService


class DestinationService:
    def __init__(self, db: Session):
        self.db = db
        self.destinations = DestinationRepository(db)
        self.categories = CategoryRepository(db)

    def _validate_categories(self, category_ids: list[int]):
        if not category_ids:
            return
        stmt = select(Category.id).where(Category.id.in_(category_ids))
        rows = self.db.execute(stmt).scalars().all()
        if len(rows) != len(set(category_ids)):
            raise AppError("VALIDATION_ERROR", "Invalid category_ids", status_code=400)

    def _normalize_destination_data(self, data: dict) -> dict:
        normalized = dict(data)

        rating = normalized.pop("rating", None)
        if rating is not None and normalized.get("rating_avg") in (None, 0):
            try:
                normalized["rating_avg"] = float(rating)
            except (TypeError, ValueError):
                pass

        price = normalized.pop("price", None)
        if isinstance(price, dict):
            level = price.get("level")
            raw_text = price.get("raw_text")
            if level and not normalized.get("price_level"):
                normalized["price_level"] = level
            if raw_text and not normalized.get("price_raw_text"):
                normalized["price_raw_text"] = raw_text
        elif isinstance(price, str):
            price_text = price.strip()
            if price_text and not normalized.get("price_raw_text"):
                normalized["price_raw_text"] = price_text

        open_hours = normalized.pop("open_hours", None)
        if isinstance(open_hours, dict):
            raw_text = open_hours.get("raw_text")
            open_text = open_hours.get("open")
            close_text = open_hours.get("close")
            if raw_text and not normalized.get("open_hours_raw_text"):
                normalized["open_hours_raw_text"] = raw_text
            if open_text and not normalized.get("open_hour_open"):
                normalized["open_hour_open"] = open_text
            if close_text and not normalized.get("open_hour_close"):
                normalized["open_hour_close"] = close_text
            if raw_text and not normalized.get("open_hour"):
                normalized["open_hour"] = raw_text

        img_value = normalized.get("img_url")
        if isinstance(img_value, list):
            clean = [str(item).strip() for item in img_value if str(item).strip()]
            normalized["img_urls"] = clean or None
            normalized["img_url"] = clean[0] if clean else None
        elif isinstance(img_value, str):
            normalized["img_url"] = img_value.strip() or None

        img_urls_value = normalized.get("img_urls")
        if isinstance(img_urls_value, list):
            clean = [str(item).strip() for item in img_urls_value if str(item).strip()]
            normalized["img_urls"] = clean or None
            if clean and not normalized.get("img_url"):
                normalized["img_url"] = clean[0]

        image_value = normalized.pop("image", None)
        if isinstance(image_value, list):
            clean = [str(item).strip() for item in image_value if str(item).strip()]
            if clean and not normalized.get("img_urls"):
                normalized["img_urls"] = clean
            if clean and not normalized.get("img_url"):
                normalized["img_url"] = clean[0]

        maps_url_value = normalized.pop("maps_url", None)
        if isinstance(maps_url_value, str):
            maps_url_value = maps_url_value.strip()
            if maps_url_value and not normalized.get("url_map"):
                normalized["url_map"] = maps_url_value

        normalized.pop("category", None)
        normalized.pop("reviews", None)
        normalized.pop("website", None)
        normalized.pop("phone", None)

        return normalized

    @staticmethod
    def _normalize_category_key(name: str) -> str:
        text = unicodedata.normalize("NFKD", name)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _slugify(name: str) -> str:
        text = unicodedata.normalize("NFKD", name)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"[\s_-]+", "-", text)
        text = re.sub(r"^-+|-+$", "", text)
        return text or "category"

    def _next_available_destination_slug(self, base: str, reserved: set[str] | None = None) -> str:
        candidate_base = self._slugify(base) or "destination"
        candidate = candidate_base
        suffix = 2
        reserved = reserved or set()
        while candidate in reserved or self.destinations.get_by_slug(candidate):
            candidate = f"{candidate_base}-{suffix}"
            suffix += 1
        return candidate

    def _ensure_destination_slug(self, data: dict, reserved: set[str] | None = None) -> str:
        raw_slug = data.get("slug")
        if isinstance(raw_slug, str) and raw_slug.strip():
            normalized = self._slugify(raw_slug)
            if not normalized:
                raise AppError("VALIDATION_ERROR", "Invalid slug", status_code=400)
            data["slug"] = normalized
            if reserved is not None and normalized in reserved:
                raise AppError("VALIDATION_ERROR", f"Duplicate slug in request payload: {normalized}", status_code=400)
            if self.destinations.get_by_slug(normalized):
                raise AppError("CONFLICT", f"Slug already exists: {normalized}", status_code=409)
            if reserved is not None:
                reserved.add(normalized)
            return normalized

        seed = str(data.get("name") or data.get("place_id") or "destination").strip()
        generated = self._next_available_destination_slug(seed, reserved)
        data["slug"] = generated
        if reserved is not None:
            reserved.add(generated)
        return generated

    def _ensure_category_by_name(self, name: str, cache: dict[str, Category]) -> Category:
        key = self._normalize_category_key(name)
        if not key:
            raise AppError("VALIDATION_ERROR", "Invalid category name", status_code=400)

        existing = cache.get(key)
        if existing:
            return existing

        base_slug = self._slugify(name)
        candidate = base_slug
        suffix = 2
        while self.categories.get_by_slug(candidate):
            candidate = f"{base_slug}-{suffix}"
            suffix += 1

        created = self.categories.create(name=name.strip(), slug=candidate, descriptions=None)
        cache[key] = created
        return created

    def _resolve_category_ids(self, category_ids: list[int] | None, category_names: list[str] | None) -> list[int]:
        resolved_ids = list(category_ids or [])

        category_cache: dict[str, Category] = {}
        for category in self.categories.list():
            key = self._normalize_category_key(category.name)
            if key:
                category_cache[key] = category

        for name in category_names or []:
            if not isinstance(name, str):
                continue
            cleaned_name = name.strip()
            if not cleaned_name:
                continue
            category = self._ensure_category_by_name(cleaned_name, category_cache)
            resolved_ids.append(int(category.id))

        deduped = sorted(set(resolved_ids))
        self._validate_categories(deduped)
        return deduped

    def _apply_reviews_to_insight(self, destination_id: int, reviews: list[dict] | None):
        if not reviews:
            return
        insight_service = InsightService(self.db)
        for review in reviews:
            if not isinstance(review, dict):
                continue
            rating_raw = review.get("rating")
            comment = review.get("text")
            if rating_raw is None:
                continue
            try:
                rating_score = int(float(rating_raw))
            except (TypeError, ValueError):
                continue
            rating_score = max(1, min(5, rating_score))
            insight_service.apply_rating_update(
                destination_id=destination_id,
                new_score=rating_score,
                new_comment=comment,
                is_new_rating=True,
            )

    def create(self, data: dict, category_ids: list[int]):
        self._validate_categories(category_ids)
        normalized_data = self._normalize_destination_data(data)
        self._ensure_destination_slug(normalized_data)
        destination = self.destinations.create(normalized_data)
        if category_ids:
            self.destinations.set_categories(destination, category_ids)
        InsightService(self.db).initialize_for_destination(destination.id)
        invalidate_destination_cache(destination.id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return destination

    def create_many(self, destinations_payload: list[dict]):
        if not destinations_payload:
            return []

        created_destinations = []
        reserved_slugs: set[str] = set()
        for item in destinations_payload:
            data = dict(item)
            category_ids = data.pop("category_ids", [])
            category_names = data.pop("category", [])
            reviews = data.pop("reviews", [])
            resolved_category_ids = self._resolve_category_ids(category_ids, category_names)
            normalized_data = self._normalize_destination_data(data)
            self._ensure_destination_slug(normalized_data, reserved_slugs)
            destination = self.destinations.create(normalized_data)
            if resolved_category_ids:
                self.destinations.set_categories(destination, resolved_category_ids)
            InsightService(self.db).initialize_for_destination(destination.id)
            self._apply_reviews_to_insight(destination.id, reviews)
            created_destinations.append(destination)

        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        for destination in created_destinations:
            invalidate_destination_cache(destination.id)
        return created_destinations

    def update(self, destination_id: int, data: dict, category_ids: list[int] | None):
        destination = self.destinations.get_by_id(destination_id)
        if not destination:
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        normalized_data = self._normalize_destination_data(data)
        destination = self.destinations.update(destination, normalized_data)
        if category_ids is not None:
            self._validate_categories(category_ids)
            self.destinations.set_categories(destination, category_ids)
        invalidate_destination_cache(destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return destination

    def delete(self, destination_id: int):
        destination = self.destinations.get_by_id(destination_id)
        if not destination:
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        self.destinations.delete(destination)
        invalidate_destination_cache(destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()

    def get_detail(self, destination_id: int, increment_view: bool = True):
        destination = self.destinations.get_detail_by_id(destination_id)
        if not destination or destination.status != "active":
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        if increment_view:
            destination.view_count += 1
            self.db.flush()
        return destination
