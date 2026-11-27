# Báo cáo Pha B — Search + Async (BE 1.2.0)

Ngày: 2026-11-27 | Lựa chọn owner: **Elasticsearch + Redis Streams** | Trạng thái: **HOÀN THÀNH**

## 1. Việc đã làm

Backend (`backend/`):
- `services/search.py` (mới): ES client lazy + ping, `ensure_index`
  (mapping name/address/description text, slug/price/categories/status keyword),
  `index_destination`, `search_ids` trả `(ids, es_used)`.
- `services/events.py` (mới): Redis Streams `travel-events` (`xadd/xread`),
  fire-and-forget (Redis down → false + warn, request không block).
- `scripts/worker.py` (mới) + service `worker` trong compose:
  changed → index ES + rebuild insight; viewed/favorite/rating → rebuild insight;
  rating → reindex ES. `final_data` đầy đủ 8 keys.
- `scripts/reindex.py` (mới): index toàn bộ active destinations.
- Routers đấu nối: `destinations/search` (ES trước, fallback DB LIKE,
  `meta.search_engine`); detail publish `destination.viewed`;
  interaction publish favorite/rating; admin publish `destination.changed`.
- `requirements.txt` += `elasticsearch==8.15.0`; `config.py` +=
  `ES_URL/ES_ENABLED/ES_INDEX/EVENTS_STREAM/EVENTS_ENABLED`;
  `Dockerfile` COPY `scripts/` (để worker/reindex chạy trong image).
- `tests/test_phase_b.py` (mới, 4 tests) + fix `test_admin` idempotent (uuid suffix).

Frontend (`frontend/`):
- `DestinationController@index`: `?q=` → gọi `destinations/search`, else list cũ.
- `destinations/index.blade.php`: hiển thị nguồn tìm kiếm (Elasticsearch/DB).

Infra: compose += `elasticsearch:8.15.0` (single-node, `xpack.security=false`,
volume `esdata`, healthcheck) + `worker` (depends postgres/redis/ES healthy).
Backend env += `ES_URL=http://elasticsearch:9200`, `ES_ENABLED=true`.
Tổng: **7 services** (postgres, redis, elasticsearch, backend, frontend, api-gateway, worker).

## 2. Verification

| Check | Kết quả |
|---|---|
| Backend pytest trong container compose | **17 passed** (13 + 4 Pha B) |
| Frontend phpunit | **12 passed, 39 assertions** |
| Smoke P3 qua gateway | **5/5** (không regression) |
| Search E2E `?q=My Khe` | `search_engine=elasticsearch` qua gateway |
| Pipeline event | `detail(2)` → insight cũ sync → 8s sau worker enrich thành `status ok + summary` |
| Reindex | `indexed 13/13` |

## 3. Gaps / quyết định còn mở

- Redis Streams giữ messages (XLEN không giảm — đúng semantics stream; chưa đặt retention/XTRIM ngoài `maxlen=10000` khi publish).
- ES single-node, chưa TLS/auth nội bộ — xử lý ở Pha C (hardening).
- Audit mới ghi `bulk_create` — bổ sung ở Pha C.
- U1..U7 trong `STANDARDS-PROFILE.md` vẫn mở.

## 4. Tiếp theo

**Pha C — Hardening + Observability**: rate-limit gateway, security headers,
auth audit đầy đủ, runbook vận hành. Cần owner chốt ngưỡng rate-limit nếu khác
mặc định (IP 120/phút, user 60/phút).
