from __future__ import annotations

import json
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

_producer = None


def _import_kafka():
    try:
        from kafka import KafkaConsumer, KafkaProducer  # type: ignore
    except Exception as exc:
        logger.warning("Kafka module unavailable: %s", exc)
        return None, None
    return KafkaConsumer, KafkaProducer


def get_producer():
    global _producer
    if not settings.kafka_enabled:
        return None
    if _producer is not None:
        return _producer

    _, kafka_producer_cls = _import_kafka()
    if kafka_producer_cls is None:
        return None

    try:
        _producer = kafka_producer_cls(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.kafka_client_id,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
            acks="all",
            retries=3,
            linger_ms=10,
        )
    except Exception as exc:
        logger.warning("Kafka producer init failed: %s", exc)
        _producer = None
    return _producer


def publish_event(topic: str, event: dict[str, Any]) -> bool:
    producer = get_producer()
    if producer is None:
        return False
    try:
        producer.send(topic, event)
        producer.flush(timeout=2)
        return True
    except Exception as exc:
        logger.warning("Kafka publish failed topic=%s error=%s", topic, exc)
        return False


def get_consumer(topics: list[str], group_id: str | None = None):
    if not settings.kafka_enabled:
        return None
    kafka_consumer_cls, _ = _import_kafka()
    if kafka_consumer_cls is None:
        return None
    try:
        return kafka_consumer_cls(
            *topics,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=group_id or settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            consumer_timeout_ms=1000,
            client_id=f"{settings.kafka_client_id}-consumer",
        )
    except Exception as exc:
        logger.warning("Kafka consumer init failed: %s", exc)
        return None
