# Boundary + Contract Inventory (XSTD-001-R001/R002)

Version: 0.1.0 | Date: 2026-11-27 | Status: inspection only (no code changed).
Contract docs: `BE-API-0.1.0.md` (T5), `FE-0.1.0.md` (T6) — to be written.

| # | Boundary | Producer | Consumer | Owner | Contract | Evidence |
|---|----------|----------|----------|-------|----------|----------|
| B1 | Browser ↔ Laravel frontend (`/`, `/destinations`, `/admin/*`) | frontend (Blade) | browser user | Unassigned (U4) | `documents/contracts/FE-0.1.0.md` (T6) | `frontend/routes/web.php`, `resources/views/**` |
| B2 | Laravel ↔ Gateway (`API_BASE_URL` → `:8080/api/v1/*`) | 5 FastAPI services via Nginx | `ApiClient.php` | Unassigned (U4) | `BE-API-0.1.0.md` (T5) | `frontend/app/Services/ApiClient.php`, `nginx.conf` |
| B3 | Gateway → auth-service (`/api/v1/auth/*`) | auth-service (`app/apps/auth_service.py`) | api-gateway | Unassigned (U4) | `BE-API-0.1.0.md` §Auth | `backend/app/routers/auth.py`, `nginx.conf` |
| B4 | Gateway → destination-service (`/public/*`, `/destinations/*`) | destination-service | api-gateway, B2 | Unassigned (U4) | `BE-API-0.1.0.md` §Public/Destinations | `backend/app/routers/{public,activity_public,destinations}.py` |
| B5 | Gateway → interaction-service (`/me/*`) | interaction-service | api-gateway, B2 | Unassigned (U4) | `BE-API-0.1.0.md` §Interaction | `backend/app/routers/interaction.py` |
| B6 | Gateway → admin-service (`/api/v1/admin/*`) | admin-service | api-gateway, B2 | Unassigned (U4) | `BE-API-0.1.0.md` §Admin | `backend/app/routers/admin.py` |
| B7 | Gateway → analytics-service (`/api/v1/analytics/*`) | analytics-service | api-gateway, B2 | Unassigned (U4) | `BE-API-0.1.0.md` §Analytics | `backend/app/routers/analytics.py` |
| B8 | Services → Kafka topics (`favorite|rating|destination|view-events`, DLQ) | interaction/admin/destination services | worker-service | Unassigned (U4) | code: `app/core/events.py`, `app/core/kafka_bus.py` (no versioned doc yet — gap) | `backend/app/worker/{consumer,handlers}.py` |
| B9 | Worker → Elasticsearch (`travel_destinations` index) | worker-service | elasticsearch | Unassigned (U4) | code: `app/core/search.py` (no versioned doc yet — gap) | `backend/app/worker/handlers.py` |
| B10 | Inter-service HTTP (`/internal/destinations/*`, `/internal/admin/*`) | destination/auth services | interaction/admin services | Unassigned (U4) | code: `app/routers/internal_*.py` (no versioned doc yet — gap) | `backend/app/routers/internal_*.py` |
| B11 | User → Recommendation engine (`/me/recommendations`, `/me/itinerary`) | `RecommendationService` (reads `destination_insights.final_data`) | authenticated user | `BE-API-1.3.0.md` §2.3/2.4 | `backend/app/services/recommendation.py`, `routers/interaction.py` |
| B12 | Admin bulk → external rating (`external_*` fields) | admin-service | admin user (bulk JSON tay) | `BE-API-1.3.0.md` §2.1 | `schemas/admin.py`, `services/admin.py`, migration `f7a2c9d1e3b4` |

Notes:
- Identity context (XSTD-001-R005): JWT Bearer; backend enforces via
  `get_current_user` / `require_admin`; frontend probes `admin/stats/top-views`
  to infer role — documented in T6; no client assertion is authoritative server-side.
- Error/data semantics (XSTD-001-R006): envelope `{success, data, meta, error}` —
  pinned in T5 from `backend/docs/API_REFERENCE.md` + code.
- Owners unresolved → U4/U5 in profile; compat window/approval authority unresolved (U5).
