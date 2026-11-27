# Backend API Contract — v1.2.0 (Pha B: search + async)

Scope Pha B: giữ nguyên BE 1.1.0 + search qua Elasticsearch (fallback DB LIKE),
events qua Redis Streams, worker build `destination_insights` đầy đủ.
XSTD-001-R002; BSTD-004-R001/R002/R004/R007/R009.

## 1. Không đổi envelope/guards

Envelope, `expires_in` phút, `require_admin`, `X-Internal-Key` như 1.1.0/1.0.0.

## 2. Mới so với 1.1.0

- `GET /destinations/search` — thử Elasticsearch trước, fallback DB LIKE khi ES
  tắt/down; `meta.search_engine = "elasticsearch" | "db"`. Đáp ứng
  `200` cả khi ES không có hit (data rỗng, không 5xx).
- Events (Redis Streams `travel-events`, fire-and-forget từ request):
  `destination.viewed` (detail +1 view), `favorite.added|removed`,
  `rating.upserted`, `destination.changed` (admin create/update/bulk).
  Request không block khi Redis down (publish trả false, log warn).
- Worker `backend/scripts/worker.py` (service `worker` trong compose):
  `destination.changed` → index ES + rebuild insight;
  viewed/favorite/rating → rebuild insight; `rating.upserted` → reindex ES.
  `destination_insights.final_data` đầy đủ: `status(ok|insufficient_data|missing),
  summary, rating_avg/count/sum, favorite_count, view_count, categories[]`.
- `backend/scripts/reindex.py` — index toàn bộ destinations active vào ES.
- Config mới: `ES_URL, ES_ENABLED, ES_INDEX=destinations, EVENTS_STREAM=travel-events,
  EVENTS_ENABLED`. Compose thêm services `elasticsearch` (8.15.0, single-node,
  volume `esdata`) + `worker`.

## 3. Không đổi

Bulk/analytics/internal/activities/audit như 1.1.0.

## Change history

- 1.2.0 (2026-11-27): Pha B — ES search + fallback, Redis Streams events,
  worker insights đầy đủ. Verify: pytest 17 passed container,
  search_engine=elasticsearch qua gateway, insight enrich sau event.
