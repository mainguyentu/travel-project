from __future__ import annotations

import logging
import time

from app.core.config import settings
from app.core.cache import invalidate_destination_cache, invalidate_public_landing_cache
from app.core.search import delete_destination_document, index_destination_document
from app.db.session import SessionLocal
from app.repositories.destinations import DestinationRepository
from app.services.destination_images import get_destination_image_migrator
from app.repositories.analytics import AnalyticsRepository

logger = logging.getLogger(__name__)


class EventHandlingError(Exception):
    pass


def _with_retry(fn, *args, **kwargs):
    attempts = settings.worker_retry_max + 1
    delay = settings.worker_retry_backoff_seconds
    last_exc = None

    for attempt in range(1, attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt >= attempts:
                break
            if delay > 0:
                time.sleep(delay * attempt)

    raise EventHandlingError(str(last_exc)) from last_exc


def handle_favorite_event(event: dict):
    payload = event.get("payload", {})
    destination_id = int(payload["destination_id"])
    delta = int(payload.get("delta", 1))

    db = SessionLocal()
    try:
        repo = AnalyticsRepository(db)
        repo.apply_favorite_delta(destination_id, delta)
        db.commit()
    finally:
        db.close()


def handle_rating_event(event: dict):
    payload = event.get("payload", {})
    destination_id = int(payload["destination_id"])
    old_score = payload.get("old_score")
    new_score = int(payload["new_score"])

    db = SessionLocal()
    try:
        repo = AnalyticsRepository(db)
        repo.apply_rating_upsert(destination_id, int(old_score) if old_score is not None else None, new_score)
        db.commit()
    finally:
        db.close()


def handle_view_event(event: dict):
    payload = event.get("payload", {})
    destination_id = int(payload["destination_id"])
    delta = int(payload.get("delta", 1))

    db = SessionLocal()
    try:
        repo = AnalyticsRepository(db)
        repo.apply_view_delta(destination_id, delta)
        db.commit()
    finally:
        db.close()


def _to_search_document(destination: dict) -> dict:
    categories = destination.get("categories", [])
    category_slugs = [c.get("slug") for c in categories if isinstance(c, dict) and c.get("slug")]
    return {
        "id": int(destination["id"]),
        "name": destination.get("name"),
        "slug": destination.get("slug"),
        "description": destination.get("description"),
        "address": destination.get("address"),
        "status": destination.get("status"),
        "price_level": destination.get("price_level"),
        "rating_avg": float(destination.get("rating_avg") or 0),
        "categories": category_slugs,
    }


def handle_destination_event(event: dict):
    payload = event.get("payload", {})
    event_type = event.get("event_type", "")

    if event_type.endswith("deleted"):
        delete_destination_document(int(payload["destination_id"]))
        return

    destinations = payload.get("destinations")
    if isinstance(destinations, list) and destinations:
        for destination in destinations:
            if not isinstance(destination, dict):
                continue
            _handle_destination_record(destination)
        return

    destination = payload.get("destination")
    if not isinstance(destination, dict):
        raise EventHandlingError("destination payload missing")

    _handle_destination_record(destination)


def _collect_destination_urls(destination: dict) -> list[str]:
    urls: list[str] = []
    img_urls_value = destination.get("img_urls")
    if isinstance(img_urls_value, list):
        urls.extend(str(item).strip() for item in img_urls_value if str(item).strip())

    img_url_value = destination.get("img_url")
    if isinstance(img_url_value, str):
        cleaned = img_url_value.strip()
        if cleaned and cleaned not in urls:
            urls.insert(0, cleaned)

    return urls


def _migrate_destination_images(destination: dict) -> None:
    migrator = get_destination_image_migrator()
    if not migrator.enabled:
        return
    if not migrator.configured:
        logger.warning(
            "destination_image_migrate_skipped stage=config destination_id=%s reason=missing_credentials",
            destination.get("id"),
        )
        return

    destination_id_raw = destination.get("id")
    if destination_id_raw is None:
        return

    urls = _collect_destination_urls(destination)
    if not urls:
        return

    migrated_urls, stats = migrator.migrate_urls(urls, destination_id=int(destination_id_raw))
    logger.info(
        "destination_image_migrate_worker_summary destination_id=%s processed=%s migrated=%s skipped=%s fallback=%s",
        destination_id_raw,
        stats.processed,
        stats.migrated,
        stats.skipped,
        stats.fallback,
    )

    db = SessionLocal()
    try:
        repo = DestinationRepository(db)
        record = repo.get_by_id(int(destination_id_raw))
        if record is None:
            return

        record.img_urls = migrated_urls or None
        record.img_url = migrated_urls[0] if migrated_urls else None
        db.commit()
    finally:
        db.close()

    invalidate_destination_cache(int(destination_id_raw))
    invalidate_public_landing_cache()


def _handle_destination_record(destination: dict) -> None:
    index_destination_document(_to_search_document(destination))
    _migrate_destination_images(destination)


def dispatch_event(event: dict):
    event_type = event.get("event_type", "")

    if event_type.startswith("favorite."):
        _with_retry(handle_favorite_event, event)
        return
    if event_type.startswith("rating."):
        _with_retry(handle_rating_event, event)
        return
    if event_type.startswith("destination.view"):
        _with_retry(handle_view_event, event)
        return
    if event_type.startswith("destination."):
        _with_retry(handle_destination_event, event)
        return

    logger.info("Unhandled event_type=%s", event_type)
