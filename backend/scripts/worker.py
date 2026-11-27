"""Travel worker: Redis Streams -> ES index + destination_insights (Pha B).

Reads `travel-events` stream:
  destination.viewed | favorite.added | rating.upserted | destination.changed
Effects:
  - destination.changed -> (re)index document into Elasticsearch
  - viewed/favorite/rating   -> rebuild destination_insights.final_data
Run: python scripts/worker.py [--once]
"""
from __future__ import annotations

import json
import logging
import sys

sys.path.insert(0, ".")

from app.core.config import settings  # noqa: E402
from app.db.models import Destination  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.repositories.destinations import DestinationRepository  # noqa: E402
from app.services import events as event_bus  # noqa: E402
from app.services import search as search_svc  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("travel-worker")


def build_insight(db, destination_id: int) -> dict:
    repo = DestinationRepository(db)
    dest = repo.get_detail(destination_id)
    if not dest:
        return {"status": "missing"}
    fav_count = repo.favorite_count(destination_id)
    rating_count, rating_sum = repo.rating_stats(destination_id)
    cats = [c.slug for c in repo.categories_for(destination_id)]
    avg = float(dest.rating_avg or 0)
    if rating_count == 0 and fav_count == 0 and dest.view_count < 10:
        status = "insufficient_data"
        summary = ""
    else:
        status = "ok"
        summary = (
            f"{dest.name}: {rating_count} ratings (avg {avg}), "
            f"{fav_count} favorites, {dest.view_count} views."
        )
    return {
        "status": status,
        "summary": summary,
        "rating_avg": avg,
        "rating_count": rating_count,
        "rating_sum": rating_sum,
        "favorite_count": fav_count,
        "view_count": dest.view_count,
        "categories": cats,
    }


def handle(db, event_type: str, payload: dict) -> None:
    from app.db.models import DestinationInsight

    did = payload.get("destination_id")
    if not did:
        return
    did = int(did)
    repo = DestinationRepository(db)
    if event_type == "destination.changed":
        dest = repo.get_detail(did)
        if dest and dest.status == "active":
            cats = [c.slug for c in repo.categories_for(did)]
            search_svc.index_destination({
                "id": dest.id, "name": dest.name, "slug": dest.slug,
                "address": dest.address or "", "description": dest.description or "",
                "price_level": dest.price_level, "category_slugs": cats,
                "rating_avg": float(dest.rating_avg or 0), "status": dest.status,
            })
        data = build_insight(db, did)
        row = db.get(DestinationInsight, did)
        if row:
            row.final_data = data
        else:
            db.add(DestinationInsight(destination_id=did, final_data=data))
        db.commit()
    elif event_type in ("destination.viewed", "favorite.added", "favorite.removed", "rating.upserted"):
        data = build_insight(db, did)
        row = db.get(DestinationInsight, did)
        if row:
            row.final_data = data
        else:
            db.add(DestinationInsight(destination_id=did, final_data=data))
        db.commit()
        if event_type == "rating.upserted":
            search_svc.ensure_index()
            dest = repo.get_detail(did)
            if dest and dest.status == "active":
                cats = [c.slug for c in repo.categories_for(did)]
                search_svc.index_destination({
                    "id": dest.id, "name": dest.name, "slug": dest.slug,
                    "address": dest.address or "", "description": dest.description or "",
                    "price_level": dest.price_level, "category_slugs": cats,
                    "rating_avg": float(dest.rating_avg or 0), "status": dest.status,
                })


def run_once() -> int:
    db = SessionLocal()
    try:
        search_svc.ensure_index()
        entries, _ = event_bus.read_new(last_id="0-0", count=100, block_ms=1000)
        for _eid, fields in entries:
            try:
                handle(db, fields.get("type", ""), json.loads(fields.get("data", "{}")))
            except Exception as exc:
                log.warning("handle failed: %s", exc)
                db.rollback()
        return len(entries)
    finally:
        db.close()


def run_loop() -> None:
    db = SessionLocal()
    log.info("worker start stream=%s es=%s", settings.events_stream, settings.es_url)
    search_svc.ensure_index()
    last_id = "$"
    try:
        while True:
            entries, last_id = event_bus.read_new(last_id=last_id, count=50, block_ms=5000)
            for _eid, fields in entries:
                try:
                    handle(db, fields.get("type", ""), json.loads(fields.get("data", "{}")))
                except Exception as exc:
                    log.warning("handle failed: %s", exc)
                    db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    if "--once" in sys.argv:
        n = run_once()
        print(f"processed {n}")
    else:
        run_loop()
