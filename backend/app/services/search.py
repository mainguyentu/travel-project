import logging

from app.core.config import settings

log = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client
    if not settings.es_enabled:
        return None
    try:
        from elasticsearch import Elasticsearch

        es = Elasticsearch(settings.es_url, request_timeout=5)
        if not es.ping():
            log.warning("elasticsearch ping failed: %s", settings.es_url)
            return None
        _client = es
        return es
    except Exception as exc:  # ES down -> fallback DB LIKE
        log.warning("elasticsearch unavailable (%s); fallback DB", exc)
        return None


def ensure_index() -> bool:
    es = get_client()
    if es is None:
        return False
    try:
        if not es.indices.exists(index=settings.es_index):
            es.indices.create(
                index=settings.es_index,
                body={
                    "settings": {"analysis": {"analyzer": {"default": {"type": "standard"}}}},
                    "mappings": {
                        "properties": {
                            "name": {"type": "text"},
                            "address": {"type": "text"},
                            "description": {"type": "text"},
                            "slug": {"type": "keyword"},
                            "price_level": {"type": "keyword"},
                            "category_slugs": {"type": "keyword"},
                            "rating_avg": {"type": "float"},
                            "status": {"type": "keyword"},
                        }
                    },
                },
            )
        return True
    except Exception as exc:
        log.warning("ensure_index failed: %s", exc)
        return False


def index_destination(doc: dict) -> bool:
    es = get_client()
    if es is None:
        return False
    try:
        es.index(index=settings.es_index, id=str(doc["id"]), document=doc, refresh="wait_for")
        return True
    except Exception as exc:
        log.warning("index_destination failed: %s", exc)
        return False


def remove_destination(doc_id: int) -> bool:
    es = get_client()
    if es is None:
        return False
    try:
        es.delete(index=settings.es_index, id=str(doc_id), ignore=[404])
        return True
    except Exception as exc:
        log.warning("remove_destination failed: %s", exc)
        return False


def search_ids(q: str = "", category_slug: str | None = None, price_level: str | None = None,
               offset: int = 0, limit: int = 20) -> tuple[list[int], bool]:
    """Return (ids, es_used). Empty ids + es_used=True means ES answered with no hits."""
    es = get_client()
    if es is None:
        return [], False
    try:
        must: list[dict] = []
        if q:
            must.append({"multi_match": {"query": q, "fields": ["name^3", "address^2", "description"]}})
        filt: list[dict] = [{"term": {"status": "active"}}]
        if category_slug:
            filt.append({"term": {"category_slugs": category_slug}})
        if price_level:
            filt.append({"term": {"price_level": price_level}})
        body = {"query": {"bool": {"must": must or [{"match_all": {}}], "filter": filt}},
                "from": offset, "size": limit, "_source": False,
                "sort": ["_score", {"rating_avg": {"order": "desc"}}]}
        res = es.search(index=settings.es_index, body=body)
        ids = [int(h["_id"]) for h in res.get("hits", {}).get("hits", [])]
        return ids, True
    except Exception as exc:
        log.warning("es search failed, fallback DB: %s", exc)
        return [], False
