# Báo cáo Pha A — Parity full-scope API (BE 1.1.0 / FE 1.1.0)

Ngày: 2026-11-27 | Nhánh: A → B → C → D (đã chốt) | Trạng thái: **HOÀN THÀNH**

## 1. Mục tiêu

Khôi phục các endpoint full-scope (BE-0.1.0) đã loại ở MVP, giữ nguyên
monolith + envelope + guards MVP. Không tự chốt U1..U7.

## 2. Việc đã làm

Backend (`backend/`):
- `routers/admin.py`: `POST /destinations/bulk` (201; 400 dup payload/unknown
  categories; 409 slug tồn tại) + ghi audit; `GET /audit-logs`;
  stats top-favorites/top-ratings thêm `from/to`.
- `routers/analytics.py` (mới, `require_admin` — đóng gap NO-auth cũ):
  `summary`, `top-favorites|top-ratings` (`from/to`, `limit ≤100`), `top-views`.
- `routers/internal.py` (mới, header `X-Internal-Key`):
  `active`, `batch`, `recompute-rating-avg`, `apply-rating-insight`.
- `routers/activities.py` (mới):
  `GET /public/activities/{slug}/recommendations`
  (flag `ACTIVITY_RECOMMENDATION_ENABLED`, 404 slug lạ, 503 khi tắt flag).
- `services/admin.py`: `bulk_create_destinations()` + `audit()`;
  `repositories/destinations.py`: `top_favorites/top_ratings(from,to)`.
- `models.py` + migration `0002` (`audit_logs`); `config.py`:
  `INTERNAL_API_KEY`, `ACTIVITY_RECOMMENDATION_ENABLED`;
  `schemas/admin.py`: `DestinationBulkCreate(items 1..100)`.
- `tests/test_phase_a.py` (mới, 3 tests).

Frontend (`frontend/`):
- `AdminController`: dashboard filter from/to, `bulkStoreDestinations`,
  `auditLogs`, `activityRecommendations`.
- Routes: `POST admin/destinations/bulk`, `GET admin/audit-logs`,
  `GET /activities/{slug}`; views: `admin/audit-logs`, `activities/show`,
  bulk form + dashboard filter.
- `JourneysTest::test_admin_bulk_audit_and_activity_pages` (mới).

Contracts: `BE-API-1.1.0.md`, `FE-1.1.0.md` (mới).

## 3. Verification

| Check | Kết quả |
|---|---|
| Backend pytest trong container compose | **13 passed** (10 cũ + 3 Pha A) |
| Frontend phpunit local | **12 passed, 39 assertions** (11+1) |
| Smoke P3 qua gateway `:8080` | **5/5** (không regression) |
| E2E Pha A (analytics summary, audit-logs, internal active, activities `bien`) | pass qua gateway |

## 4. Gaps / quyết định còn mở

- Audit mới ghi `bulk_create` — các action khác (user/category/delete) bổ sung ở Pha C.
- Internal đi qua gateway chung (chưa tách network riêng) — xử lý ở Pha C/D.
- U1..U7 trong `STANDARDS-PROFILE.md` vẫn mở.

## 5. Tiếp theo

**Pha B — Search + Async** (ES/OpenSearch, Kafka/worker, `destination_insights` đầy đủ).
Cần owner chốt: ES vs OpenSearch; Kafka vs Redis Streams.
