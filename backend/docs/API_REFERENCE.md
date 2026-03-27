# API Reference (Backend)

Tài liệu này mô tả các endpoint chính của backend FastAPI.

## Base URL

- Local monolith: `http://localhost:8000`
- Gateway (docker-compose): `http://localhost:8080`
- API prefix: `/api/v1`

## Response Format

### Success

```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "...",
    "timestamp": "2026-01-01T00:00:00+00:00"
  }
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": []
  },
  "meta": {
    "request_id": "...",
    "timestamp": "2026-01-01T00:00:00+00:00"
  }
}
```

## Health

- `GET /health`

## Auth

### Register

- `POST /api/v1/auth/register`
- Body:

```json
{
  "name": "User",
  "email": "user@example.com",
  "password": "User@123"
}
```

### Login

- `POST /api/v1/auth/login`
- Body:

```json
{
  "email": "user@example.com",
  "password": "User@123"
}
```

- Trả về `access_token`, `refresh_token`, `token_type`, `expires_in`.
- `token_type` hiện tại trả về giá trị `Bearer`.

### Refresh Token

- `POST /api/v1/auth/refresh`
- Body:

```json
{
  "refresh_token": "..."
}
```

### Logout

- `POST /api/v1/auth/logout`
- Body:

```json
{
  "refresh_token": "..."
}
```

## Public

### Landing

- `GET /api/v1/public/landing`
- Trả về: `highlights`, `categories`, `top_ratings`, `top_favorites`.

## Destinations

### List Destinations

- `GET /api/v1/destinations`
- Query params:
  - `category_slug` (optional)
  - `price_level` (optional)
  - `rating_min` (optional)
  - `keyword` (optional)
  - `sort` (optional)
  - `page` (default 1)
  - `limit` (default 20, max 100)

### Search Destinations

- `GET /api/v1/destinations/search`
- Query params:
  - `q` (default empty)
  - `category_slug` (optional)
  - `price_level` (optional)
  - `page` (default 1)
  - `limit` (default 20, max 100)

### Destination Detail

- `GET /api/v1/destinations/{destination_id}`
- Tự động tăng `view_count` khi xem chi tiết.

## Interaction (Cần Bearer Token)

Header mẫu:

```http
Authorization: Bearer <access_token>
```

### Favorite Destination

- `POST /api/v1/me/favorites/{destination_id}`

### Unfavorite Destination

- `DELETE /api/v1/me/favorites/{destination_id}`

### List Favorites

- `GET /api/v1/me/favorites`
- Query params: `page`, `limit`

### Upsert Rating

- `PUT /api/v1/me/ratings/{destination_id}`
- Body:

```json
{
  "rating_score": 5,
  "comment": "Great"
}
```

### Get My Rating

- `GET /api/v1/me/ratings/{destination_id}`

## Admin (Cần Bearer Token + role admin)

### Users

- `GET /api/v1/admin/users?page=1&limit=20`
- `PATCH /api/v1/admin/users/{user_id}/status`
- `PATCH /api/v1/admin/users/{user_id}/role`

Body update status:

```json
{
  "status": "active"
}
```

Body update role:

```json
{
  "role": "admin"
}
```

### Categories

- `GET /api/v1/admin/categories`
- `POST /api/v1/admin/categories`
- `PUT /api/v1/admin/categories/{category_id}`
- `DELETE /api/v1/admin/categories/{category_id}`

Body create/update:

```json
{
  "name": "Am thuc",
  "slug": "food",
  "descriptions": "Quan an"
}
```

### Destinations

- `GET /api/v1/admin/destinations?status=active&page=1&limit=20`
- `POST /api/v1/admin/destinations`
- `PUT /api/v1/admin/destinations/{destination_id}`
- `DELETE /api/v1/admin/destinations/{destination_id}`

Body create mẫu:

```json
{
  "name": "My Khe Beach",
  "slug": "my-khe-beach",
  "address": "Vo Nguyen Giap, Da Nang",
  "description": "Bai bien noi tieng",
  "price_level": "medium",
  "open_hour": "All day",
  "img_url": "https://example.com/mykhe.jpg",
  "url_map": "https://maps.google.com",
  "lat": 16.0595,
  "lng": 108.2466,
  "status": "active",
  "category_ids": [1, 2]
}
```

### Admin Stats

- `GET /api/v1/admin/stats/top-favorites`
- `GET /api/v1/admin/stats/top-ratings`
- `GET /api/v1/admin/stats/top-views`

## Swagger / OpenAPI

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

Ví dụ qua gateway:

- `http://localhost:8080/docs`
- `http://localhost:8080/openapi.json`
