from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings
from app.core.kafka_bus import get_consumer, publish_event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay events from DLQ back to business topics")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of events to replay")
    parser.add_argument("--from-topic", default=settings.kafka_dlq_topic, help="Source DLQ topic")
    parser.add_argument("--group-id", default="travel-dlq-replay", help="Consumer group id")
    parser.add_argument("--event-prefix", default=None, help="Optional event_type prefix filter")
    parser.add_argument("--dry-run", action="store_true", help="Do not publish, only print matching events")
    return parser.parse_args()


def resolve_target_topic(event_type: str) -> str | None:
    if event_type.startswith("favorite."):
        return settings.kafka_topic_favorite
    if event_type.startswith("rating."):
        return settings.kafka_topic_rating
    if event_type.startswith("destination.view"):
        return settings.kafka_topic_view
    if event_type.startswith("destination."):
        return settings.kafka_topic_destination
    return None


def run() -> int:
    args = parse_args()
    if args.limit <= 0:
        print("--limit must be > 0")
        return 1

    consumer = get_consumer([args.from_topic], group_id=args.group_id)
    if consumer is None:
        print("Kafka consumer unavailable. Check KAFKA_ENABLED and kafka connectivity.")
        return 1

    scanned = 0
    replayed = 0
    skipped = 0
    failed = 0

    try:
        for message in consumer:
            event = message.value
            scanned += 1
            event_type = str(event.get("event_type", ""))

            if args.event_prefix and not event_type.startswith(args.event_prefix):
                skipped += 1
                continue

            target_topic = resolve_target_topic(event_type)
            if not target_topic:
                skipped += 1
                continue

            if args.dry_run:
                print(f"[dry-run] {event_type} -> {target_topic}")
                replayed += 1
            else:
                ok = publish_event(target_topic, event)
                if ok:
                    replayed += 1
                    consumer.commit()
                    print(f"[replayed] {event_type} -> {target_topic}")
                else:
                    failed += 1
                    print(f"[failed] {event_type} -> {target_topic}")

            if replayed >= args.limit:
                break
    finally:
        consumer.close()

    print(
        "Replay summary:",
        f"scanned={scanned}",
        f"replayed={replayed}",
        f"skipped={skipped}",
        f"failed={failed}",
    )

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(run())
