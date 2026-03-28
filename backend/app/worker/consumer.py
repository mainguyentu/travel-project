from __future__ import annotations

import logging
import time

from app.core.config import settings
from app.core.kafka_bus import get_consumer, publish_event
from app.worker.handlers import EventHandlingError, dispatch_event

logger = logging.getLogger(__name__)


def _topics() -> list[str]:
    return [
        settings.kafka_topic_favorite,
        settings.kafka_topic_rating,
        settings.kafka_topic_destination,
        settings.kafka_topic_view,
    ]


def run_forever():
    consumer = get_consumer(_topics())
    if consumer is None:
        logger.warning("Kafka consumer disabled or unavailable; worker sleeping")
        while True:
            time.sleep(60)

    logger.info("Worker started with topics=%s", _topics())

    while True:
        try:
            for message in consumer:
                event = message.value
                try:
                    dispatch_event(event)
                    consumer.commit()
                except EventHandlingError as exc:
                    logger.error("Worker event handling failed: %s", exc)
                    publish_event(settings.kafka_dlq_topic, event)
                    consumer.commit()
                except Exception as exc:
                    logger.exception("Worker unexpected error: %s", exc)
                    publish_event(settings.kafka_dlq_topic, event)
                    consumer.commit()
        except Exception as exc:
            logger.exception("Worker loop error: %s", exc)
            time.sleep(2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_forever()
