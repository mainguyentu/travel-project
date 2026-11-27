# Backend API Contract v0.1.0 (XSTD-001-R002, BSTD-004-R001)

Base: `/api/v1` (`backend/app/core/config.py:12`). Gateway: `nginx.conf`.
Source of truth in code: `backend/app/routers/*.py`; human reference:
`backend/docs/API_REFERENCE.md`.

## 1. Envelope (BSTD-004-R009, XSTD-001-R006)

Success: `{success:true, data, meta:{request_id, timestamp}}`.
Error: `{success:false, error:{code, message, details}, meta:{request_id, timestamp}}`.
`expires_in` unit: **unresolved** (config `jwt_access_ttl_min=30` / `jwt_refresh_ttl_days=14`
vs docs claiming seconds/minutes inconsistently — see checklist item B3).

## 2. Operations

### Auth (`/auth`, public, no auth; body `{refresh_token}` for refresh/logout)
- `POST /auth/register` (201) `{name, email, password}`
- `POST /auth/login` (200) `{email, password}` → `{access_token, refresh_token, token_type: Bearer, expires_in}`
- `POST /auth/refresh` (200) `{refresh_token}`
- `POST /auth/logout` (200) `{refresh_token}` (revoke)

### Public (no auth)
- `GET /public/landing` → `{highlights[6], categories, top_ratings[6], top_favorites[6]}`
- `GET /public/activities/{slug}/recommendations` (`page=1`, `limit=10 max100`, `budget_level?`)
  → `{activity, highlight_destinations, recommended_destinations, trending, error_info}`
  fallback error code `ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR`.
  Flag: `activity_recommendation_endpoint_enabled` (default true).

### Destinations (no auth)
- `GET /destinations` (`category_slug, price_level, rating_min, keyword, sort, page=1, limit=20`)
- `GET /destinations/search` (`q, category_slug, price_level, page, limit`) — ES if enabled else DB fallback
- `GET /destinations/{id}` — increments `view_count`, publishes `destination.viewed`; returns `+insight +metrics`

### Interaction (`/me`, Bearer user via `get_current_user`)
- `POST /me/favorites/{id}` (idempotent) / `DELETE /me/favorites/{id}` / `GET /me/favorites?page&limit`
- `PUT /me/ratings/{id}` `{rating_score 1..5, comment?}` (upsert) / `GET /me/ratings/{id}` (null when none)

### Admin (`/admin`, `require_admin` — role `admin`)
- Users: `GET /admin/users`, `PATCH /admin/users/{id}/status {active|locked}`, `PATCH .../role {user|admin}`
- Categories: `GET|POST /admin/categories`, `PUT|DELETE /admin/categories/{id}`
- Destinations: `GET /admin/destinations`, `POST /admin/destinations`,
  `POST /admin/destinations/bulk` (400 duplicate slug in payload / 409 slug exists),
  `PUT|DELETE /admin/destinations/{id}`
- Stats: `GET /admin/stats/top-favorites|top-ratings|top-views`

### Analytics (`/analytics`, NO auth in code — known gap, BSTD-007-R003)
- `GET /analytics/summary`, `GET /analytics/top-favorites|top-ratings|top-views?limit=10`

### Internal service-to-service (not via gateway)
- No-auth: `GET /internal/destinations/{id}/active`, `POST /internal/destinations/batch`,
  `POST /internal/destinations/{id}/{apply-rating-insight,recompute-rating-avg}`
- Admin-JWT: `/internal/admin/users|/categories|/destinations` (mirror of admin CRUD + bulk)

## 3. Identity (BSTD-004-R007, XSTD-001-R005)

JWT Bearer `Authorization`. Access TTL 30 min, refresh 14 days (config).
Backend enforces; client assertions never authoritative (BSTD-007-R003).
Exceptions: `/analytics/*` and `/internal/destinations/*` currently unenforced — recorded as gaps.

## 4. Pagination/ordering/nullability (XSTD-001-R006)

`page` default 1, `limit` default 20 (destinations) / 10 (analytics top-*); max 100 on
recommendations. Ordering via `sort`. `GET /me/ratings/{id}` returns `data: null` when absent.
`limit` upper bound not enforced on all list endpoints — gap → T7 (BSTD-004-R005).

## 5. Compatibility (BSTD-004-R004)

No versioning policy documented beyond URL prefix `/api/v1`; additive fields only by
convention. Breaking-change procedure: **unresolved** (U5). Consumers: Laravel `ApiClient`
(B2) + 5 gateway upstreams; check `documents/contracts/BOUNDARIES.md` B1..B10 before change.

## Change history

- 0.1.0 (2026-11-27): Initial versioned contract derived from code inspection.
