from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

_es_client = None


def _import_es_client():
    try:
        from elasticsearch import Elasticsearch  # type: ignore
    except Exception as exc:
        logger.warning("Elasticsearch module unavailable: %s", exc)
        return None
    return Elasticsearch


def get_es_client():
    global _es_client
    if not settings.elasticsearch_enabled:
        return None
    if _es_client is not None:
        return _es_client

    cls = _import_es_client()
    if cls is None:
        return None

    try:
        _es_client = cls(settings.elasticsearch_url)
        return _es_client
    except Exception as exc:
        logger.warning("Elasticsearch init failed: %s", exc)
        _es_client = None
        return None


def ensure_destination_index() -> None:
    es = get_es_client()
    if es is None:
        return

    index = settings.elasticsearch_index
    try:
        if es.indices.exists(index=index):
            return
        es.indices.create(
            index=index,
            mappings={
                "properties": {
                    "id": {"type": "long"},
                    "name": {"type": "text"},
                    "slug": {"type": "keyword"},
                    "description": {"type": "text"},
                    "address": {"type": "text"},
                    "status": {"type": "keyword"},
                    "price_level": {"type": "keyword"},
                    "rating_avg": {"type": "float"},
                    "categories": {"type": "keyword"},
                }
            },
        )
    except Exception as exc:
        logger.warning("Elasticsearch index ensure failed: %s", exc)


def index_destination_document(document: dict[str, Any]) -> None:
    es = get_es_client()
    if es is None:
        return
    ensure_destination_index()
    try:
        es.index(index=settings.elasticsearch_index, id=str(document["id"]), document=document)
    except Exception as exc:
        logger.warning("Elasticsearch index failed: %s", exc)


def delete_destination_document(destination_id: int) -> None:
    es = get_es_client()
    if es is None:
        return
    try:
        es.delete(index=settings.elasticsearch_index, id=str(destination_id), ignore=[404])
    except Exception as exc:
        logger.warning("Elasticsearch delete failed: %s", exc)


def search_destination_ids(
    q: str,
    category_slug: str | None,
    price_level: str | None,
    page: int,
    limit: int,
) -> list[int] | None:
    es = get_es_client()
    if es is None:
        return None

    ensure_destination_index()
    offset = (page - 1) * limit
    must: list[dict[str, Any]] = []
    filters: list[dict[str, Any]] = [{"term": {"status": "active"}}]

    if q:
        must.append(
            {
                "multi_match": {
                    "query": q,
                    "fields": ["name^3", "description", "address"],
                }
            }
        )
    if category_slug:
        filters.append({"term": {"categories": category_slug}})
    if price_level:
        filters.append({"term": {"price_level": price_level}})

    query: dict[str, Any] = {"bool": {"filter": filters}}
    if must:
        query["bool"]["must"] = must

    try:
        resp = es.search(
            index=settings.elasticsearch_index,
            query=query,
            from_=offset,
            size=limit,
            sort=[{"_score": {"order": "desc"}}],
        )
        hits = resp.get("hits", {}).get("hits", [])
        ids: list[int] = []
        for hit in hits:
            src = hit.get("_source", {})
            item_id = src.get("id")
            if item_id is not None:
                ids.append(int(item_id))
        return ids
    except Exception as exc:
        logger.warning("Elasticsearch search failed: %s", exc)
        return None
