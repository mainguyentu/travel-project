# Frontend Contract — MVP v1.0.0 (rewrite 2026-11-27)

Scope P2: Laravel 11 + Blade, phục vụ MVP lõi. Kế thừa `FE-0.1.0.md`,
loại bỏ ngoài-MVP. FSTD-004-R001/R003, FSTD-005-R001, XSTD-001-R005.

## 1. Routes

| Method | URI | Controller | Guard | Backend call |
|--------|-----|-----------|-------|--------------|
| GET | `/` | HomeController@index | — | `public/landing` |
| GET | `/destinations` | DestinationController@index | — | `destinations?page&limit=15&...` + `public/landing` (filters) |
| GET/POST | `/login`, `/register` | AuthController | `guest` | `auth/login`, `auth/register` |
| POST | `/logout` | AuthController@logout | `session.auth` | `auth/logout {refresh_token}` |
| GET | `/profile`, `/my-favorites` | ProfileController | `session.auth` | `me/favorites` |
| POST/DELETE | `/favorites/{id}` | ProfileController | `session.auth` | `me/favorites/{id}` |
| PUT | `/ratings/{id}` | ProfileController@rate | `session.auth` | `me/ratings/{id}` |
| GET | `/admin`, `/admin/users|categories|destinations|stats` (+PATCH/POST/PUT/DELETE) | AdminController | `session.admin` | `admin/*` mirror |

Không `GET /destinations/{id}` (detail = JS modal → `GET /api/v1/destinations/{id}`).
Không `/admin/login` (chung `/login` + probe role `GET admin/stats/top-views`).
Không activity tabs (pha async — landing chỉ highlights/categories/top).

## 2. Views

Layouts: `layouts/{app,public,admin}.blade.php`.
Components: `admin-sidebar/topbar, alert, destination-card,
destination-detail-modal, filter-panel, footer, navbar, pagination, rating-form`.
Pages: public `home, destinations/index, auth/{login,register}, profile, favorites`;
admin `dashboard, stats, users/index, categories/index, destinations/index`.

## 3. State (FSTD-005-R001)

- Authoritative: backend. Client chỉ giữ `Session access_token/refresh_token/user`.
- ApiClient GET-cache có TTL theo prefix, invalidate-on-write.
- 401 (non-`auth/*`) → `POST auth/refresh` → retry 1 lần → else clear session.

## 4. Identity (XSTD-001-R005)

Login lưu token pair; role suy ra bằng probe `admin/stats/top-views`.
`session.admin` guard `/admin/*`. Backend re-enforce mỗi request.

## Change history

- 1.0.0 (2026-11-27): Tách từ FE-0.1.0 cho rewrite MVP; bỏ activity tabs,
  giữ nguyên route/guard/state đã kiểm chứng.
