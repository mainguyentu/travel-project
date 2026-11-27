# Frontend Contract / Inventory v0.1.0 (FSTD-004-R001/R003, FSTD-005-R001, XSTD-001-R005)

Source: `frontend/routes/web.php`, `app/Http/Controllers/*.php`,
`app/Services/ApiClient.php`, `resources/views/**`.

## 1. Routes (FSTD-004-R001 — module responsibilities)

| Method | URI | Controller | Middleware | Backend call |
|--------|-----|-----------|------------|--------------|
| GET | `/` | HomeController@index | — | `public/landing` + `public/activities/{slug}/recommendations?page=1&limit=3` (flag-gated), `me/favorites?limit=100` (if logged in) |
| GET | `/destinations` | DestinationController@index | — | `destinations?page&limit=15&...` + `public/landing` (filters) |
| GET/POST | `/login`, `/register` | AuthController | `guest` | `auth/login`, `auth/register` |
| POST | `/logout` | AuthController@logout | `session.auth` | `auth/logout {refresh_token}` |
| GET | `/profile`, `/my-favorites` | ProfileController | `session.auth` | `me/favorites` (favorites) |
| POST/DELETE | `/favorites/{id}` | ProfileController | `session.auth` | `me/favorites/{id}` |
| PUT | `/ratings/{id}` | ProfileController@rate | `session.auth` | `me/ratings/{id}` |
| GET | `/admin`, `/admin/users|categories|destinations|stats` (+ PATCH/POST/PUT/DELETE) | AdminController | `session.admin` | `admin/*` mirror |

No `GET /destinations/{id}` route (detail = JS modal → `GET /api/v1/destinations/{id}`).
No `/admin/login` (shared `/login` + role probe `GET admin/stats/top-views`).
5 home activity tabs hardcoded: `city-tour, food-tour, chill-bien, kham-pha-thien-nhien, van-hoa-lich-su`.

## 2. Component inventory (FSTD-004-R003 — reviewable inputs)

Layouts: `layouts/{app,public,admin}.blade.php`.
Components (10): `admin-sidebar/topbar, alert, destination-card, destination-detail-modal,
filter-panel, footer, navbar, pagination, rating-form`.
Pages: public `home, destinations/index, auth/{login,register}, profile, favorites`;
admin `dashboard, stats, users/index, categories/index, destinations/index`.

## 3. State ownership (FSTD-005-R001)

- Authoritative: backend (FSTD-005-R001 MUST NOT treats client as authoritative — conforms).
- Client: `Session access_token/refresh_token/user`; ApiClient GET-cache
  (`config api.cache.*`, TTL per prefix, registry invalidate-on-write).
- Auto-refresh: 401 (non-`auth/*`) → `POST auth/refresh` → retry once → else clear session.

## 4. Identity flow (XSTD-001-R005)

Login stores token pair; role inferred by probing `admin/stats/top-views`
(admin vs user). `session.admin` guards `/admin/*`. Server re-enforces per request.
Known fragility: role inference depends on an analytics endpoint that is itself
unauthenticated in code (see `BE-API-0.1.0.md` §2) — recorded gap, not changed here.

## 5. Form behavior gaps (→ T8, FSTD-005)

Client-side constraint feedback (R002), input preservation on failure (R004),
double-submit guards (R005), unsaved-input warning (R006-SHOULD) — present
only via generic back+flash; per-form verification pending T8.

## Change history

- 0.1.0 (2026-11-27): Initial inventory from code inspection.
