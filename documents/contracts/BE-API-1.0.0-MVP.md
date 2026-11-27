# Backend API Contract — MVP v1.0.0 (rewrite 2026-11-27)

Scope P0: monolith FastAPI (`app.main:app`), gateway proxy 1 backend.
Kế thừa `documents/contracts/BE-API-0.1.0.md`, loại bỏ ngoài-MVP.
XSTD-001-R002 versioned contract; BSTD-004-R001/R002/R004/R007/R009.

## 1. Envelope (giữ nguyên)

Success: `{success:true, data, meta:{request_id, timestamp}}`.
Error: `{success:false, error:{code, message, details:[{loc,msg,type}]}, meta:{request_id, timestamp}}`.
Validation error: chỉ `{loc, msg, type}` — không `input`/`ctx` (BSTD-008-R001/R003).
`expires_in`: đơn vị **phút** (access 30, refresh 20160).

## 2. Auth (`/auth`, public)

- `POST /auth/register` (201) `{name, email, password}`
- `POST /auth/login` (200) `{email, password}` → `{access_token, refresh_token, token_type: Bearer, expires_in}`
- `POST /auth/refresh` (200) `{refresh_token}` (rotate + revoke cũ)
- `POST /auth/logout` (200) `{refresh_token}` (revoke)

## 3. Public (no auth)

- `GET /public/landing` → `{highlights[6], categories, top_ratings[6], top_favorites[6]}` (DB trực tiếp)
- `GET /destinations` (`category_slug, price_level, rating_min, keyword, sort, page=1, limit=20 max100`)
- `GET /destinations/search` (`q, category_slug, price_level, page, limit`) — DB LIKE pha đầu
- `GET /destinations/{id}` — tăng `view_count` đồng bộ, trả `+insight(final_data) +metrics(view_count, favorite_count, rating_count)`

## 4. Interaction (`/me`, Bearer user)

- `POST /me/favorites/{id}` (idempotent) / `DELETE /me/favorites/{id}` / `GET /me/favorites?page&limit`
- `PUT /me/ratings/{id}` `{rating_score 1..5, comment?}` (upsert, recompute `rating_avg` đồng bộ)
- `GET /me/ratings/{id}` (null khi chưa rating)

## 5. Admin (`/admin`, `require_admin`)

- `GET /admin/users`, `PATCH /admin/users/{id}/status {active|locked}`, `PATCH /admin/users/{id}/role {user|admin}`
- `GET|POST /admin/categories`, `PUT|DELETE /admin/categories/{id}`
- `GET|POST /admin/destinations`, `PUT|DELETE /admin/destinations/{id}`
- `GET /admin/stats/top-favorites|top-ratings|top-views` (DB trực tiếp)

## 6. Ngoài MVP (pha async — chưa implement)

`POST /admin/destinations/bulk`, `/analytics/*`, `/internal/*`,
`/public/activities/*`, Kafka/ES/worker, audit_logs, destination_metrics,
`insight_cache`, Cloudinary migrate, microservice split.

## Change history

- 1.0.0 (2026-11-27): Tách từ BE-API-0.1.0 cho rewrite MVP; chốt monolith,
  DB LIKE search, insights tối giản, expires_in phút.
