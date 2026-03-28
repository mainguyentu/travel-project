from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventType:
    FAVORITE_CREATED = "favorite.created"
    FAVORITE_DELETED = "favorite.deleted"
    RATING_UPSERTED = "rating.upserted"
    DESTINATION_CREATED = "destination.created"
    DESTINATION_UPDATED = "destination.updated"
    DESTINATION_DELETED = "destination.deleted"
    DESTINATION_VIEWED = "destination.viewed"


def build_event(event_type: str, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "occurred_at": now_iso(),
        "request_id": request_id,
        "payload": payload,
        "version": 1,
    }
