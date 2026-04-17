from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.models import Destination
from app.db.session import SessionLocal
from app.services.destination_images import get_destination_image_migrator

logger = logging.getLogger(__name__)


def _load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {"last_id": 0, "processed": 0, "migrated": 0, "skipped": 0, "fallback": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        logger.warning("backfill_checkpoint_invalid path=%s; starting from zero", str(path))
        return {"last_id": 0, "processed": 0, "migrated": 0, "skipped": 0, "fallback": 0}


def _save_checkpoint(path: Path, checkpoint: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(checkpoint)
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def _needs_migration(destination: Destination) -> bool:
    urls = destination.img_urls or []
    if destination.img_url and destination.img_url not in urls:
        urls = [destination.img_url] + urls
    if not urls:
        return False
    return any("res.cloudinary.com" not in str(url) for url in urls)


def _collect_urls(destination: Destination) -> list[str]:
    urls = []
    if isinstance(destination.img_urls, list):
        urls.extend(str(item).strip() for item in destination.img_urls if str(item).strip())
    if isinstance(destination.img_url, str) and destination.img_url.strip() and destination.img_url.strip() not in urls:
        urls.insert(0, destination.img_url.strip())
    return urls


def run_backfill(*, batch_size: int, checkpoint_file: Path, sleep_seconds: float, max_batches: int | None) -> None:
    migrator = get_destination_image_migrator()
    checkpoint = _load_checkpoint(checkpoint_file)
    last_id = int(checkpoint.get("last_id", 0))
    batches_done = 0

    logger.info(
        "destination_image_backfill_started batch_size=%s checkpoint=%s cloudinary_enabled=%s",
        batch_size,
        str(checkpoint_file),
        migrator.enabled,
    )

    while True:
        if max_batches is not None and batches_done >= max_batches:
            logger.info("destination_image_backfill_stopped reason=max_batches batches=%s", batches_done)
            break

        db = SessionLocal()
        try:
            stmt = select(Destination).where(Destination.id > last_id).order_by(Destination.id.asc()).limit(batch_size)
            rows = db.execute(stmt).scalars().all()
            if not rows:
                logger.info("destination_image_backfill_completed last_id=%s", last_id)
                break

            batch_processed = 0
            batch_migrated = 0
            batch_skipped = 0
            batch_fallback = 0

            for destination in rows:
                batch_processed += 1
                last_id = int(destination.id)

                if not _needs_migration(destination):
                    batch_skipped += 1
                    continue

                urls = _collect_urls(destination)
                migrated_urls, stats = migrator.migrate_urls(urls, destination_id=int(destination.id))
                destination.img_urls = migrated_urls or None
                destination.img_url = migrated_urls[0] if migrated_urls else None

                batch_migrated += stats.migrated
                batch_skipped += stats.skipped
                batch_fallback += stats.fallback

            db.commit()
            batches_done += 1

            checkpoint["last_id"] = last_id
            checkpoint["processed"] = int(checkpoint.get("processed", 0)) + batch_processed
            checkpoint["migrated"] = int(checkpoint.get("migrated", 0)) + batch_migrated
            checkpoint["skipped"] = int(checkpoint.get("skipped", 0)) + batch_skipped
            checkpoint["fallback"] = int(checkpoint.get("fallback", 0)) + batch_fallback
            _save_checkpoint(checkpoint_file, checkpoint)

            logger.info(
                "destination_image_backfill_batch last_id=%s processed=%s migrated=%s skipped=%s fallback=%s total_processed=%s",
                last_id,
                batch_processed,
                batch_migrated,
                batch_skipped,
                batch_fallback,
                checkpoint["processed"],
            )

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
        except Exception:  # noqa: BLE001
            db.rollback()
            logger.exception("destination_image_backfill_failed last_id=%s", last_id)
            raise
        finally:
            db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill destination images to Cloudinary")
    parser.add_argument("--batch-size", type=int, default=settings.destination_image_backfill_batch_size)
    parser.add_argument("--checkpoint-file", default=settings.destination_image_backfill_checkpoint_file)
    parser.add_argument("--sleep-seconds", type=float, default=settings.destination_image_backfill_sleep_seconds)
    parser.add_argument("--max-batches", type=int, default=None)
    return parser


def main() -> None:
    setup_logging()
    args = build_parser().parse_args()
    run_backfill(
        batch_size=args.batch_size,
        checkpoint_file=Path(args.checkpoint_file),
        sleep_seconds=args.sleep_seconds,
        max_batches=args.max_batches,
    )


if __name__ == "__main__":
    main()
