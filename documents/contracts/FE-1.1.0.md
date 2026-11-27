# Frontend Contract — v1.1.0 (Pha A: parity full-scope)

Scope Pha A: giữ nguyên FE 1.0.0 + parity cho endpoints mới của BE 1.1.0.
FSTD-004-R001/R003, FSTD-005-R001, XSTD-001-R005.

## 1. Routes mới

| Method | URI | Controller | Guard | Backend call |
|--------|-----|-----------|-------|--------------|
| POST | `/admin/destinations/bulk` | AdminController@bulkStoreDestinations | `session.admin` | `admin/destinations/bulk {items}` (form textarea JSON) |
| GET | `/admin/audit-logs` | AdminController@auditLogs | `session.admin` | `admin/audit-logs?page&limit` |
| GET | `/activities/{slug}` | AdminController@activityRecommendations | — | `public/activities/{slug}/recommendations` |
| GET | `/admin` (dashboard) | AdminController@dashboard | `session.admin` | `admin/stats/top-favorites\|top-ratings?from&to` (form date filter) |

## 2. Views mới

- `admin/audit-logs.blade.php` (bảng id/actor/action/entity/detail/thời gian).
- `activities/show.blade.php` (gợi ý + trending).
- `admin/destinations/index.blade.php` += form bulk import (details/textarea JSON).
- `admin/dashboard.blade.php` += form lọc from/to.

## 3. Không đổi

Routes/views/state/identity như FE 1.0.0 (session tokens, ApiClient cache +
refresh-and-retry, `session.admin` guard).

## Change history

- 1.1.0 (2026-11-27): Parity Pha A — bulk/audit/activities/dashboard filter.
  Verify: phpunit 12 passed/39 assertions (mới `test_admin_bulk_audit_and_activity_pages`).
