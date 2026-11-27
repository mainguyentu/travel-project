# Backend API Contract — v1.1.0 (Pha A: parity full-scope)

Scope Pha A: giữ nguyên MVP (monolith `app.main:app`) + khôi phục ngoài-MVP
từ `BE-API-0.1.0.md`: bulk, analytics (có auth), internal (key riêng),
activities, audit log. XSTD-001-R002; BSTD-004-R001/R002/R004/R007/R009.

## 1. Envelope (giữ nguyên MVP)

Success: `{success:true, data, meta:{request_id, timestamp}}`.
Error: `{success:false, error:{code, message, details:[{loc,msg,type}]}, meta:{request_id, timestamp}}`.
`expires_in`: đơn vị **phút** (access 30, refresh 20160).

## 2. Mới so với MVP 1.0.0

- `POST /admin/destinations/bulk` (admin, 201) `{items[1..100]}`
  - 400 duplicate slug trong payload / unknown categories;
    409 slug đã tồn tại; ghi `audit_logs(bulk_create)`.
- `GET /analytics/summary|top-favorites|top-ratings|top-views`
  (require_admin — đóng gap NO-auth cũ; BSTD-007-R003).
  `top-favorites|top-ratings` hỗ trợ `from/to` (ISO8601), `limit 1..100`.
- `GET /internal/destinations/{id}/active`,
  `POST /internal/destinations/batch {ids[1..100]}`,
  `POST /internal/destinations/{id}/recompute-rating-avg`,
  `POST /internal/destinations/{id}/apply-rating-insight`
  (header `X-Internal-Key == INTERNAL_API_KEY`; qua gateway giống các API khác,
  chỉ dùng nội bộ/future worker — không expose cho browser).
- `GET /public/activities/{slug}/recommendations`
  (`page=1, limit=10 max100, budget_level?`, flag
  `ACTIVITY_RECOMMENDATION_ENABLED`; 404 unknown slug,
  503 khi tắt flag với code `ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR`).
- `GET /admin/stats/top-favorites|top-ratings` thêm `from/to` (ISO8601).
- `GET /admin/audit-logs?page&limit` (admin) — đọc bảng `audit_logs`
  (migration 0002; hiện ghi `bulk_create`, các action khác bổ sung ở Pha C).

## 3. Không đổi

Auth/public/destinations/interaction/admin-CRUD như MVP 1.0.0 (envelope,
`expires_in` phút, guard `require_admin`, limit bound `le=100`).

## Change history

- 1.1.0 (2026-11-27): Pha A parity — bulk, analytics có auth + from/to,
  internal key, activities, audit_logs. Verify: pytest 13 passed container,
  phpunit 12 passed, smoke P3 5/5, E2E analytics/audit/internal/activities.
