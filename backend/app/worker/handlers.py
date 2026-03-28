from __future__ import annotations

import logging
import time

from app.core.config import settings
from app.core.search import delete_destination_document, index_destination_document
from app.db.session import SessionLocal
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

    destination = payload.get("destination")
    if not isinstance(destination, dict):
        raise EventHandlingError("destination payload missing")

    index_destination_document(_to_search_document(destination))


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
