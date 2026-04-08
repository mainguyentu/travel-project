# API Reference (Backend)

Tài liệu này mô tả các endpoint chính của backend FastAPI theo trạng thái code hiện tại.

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

Body:

```json
{
  "name": "User",
  "email": "user@example.com",
  "password": "User@123"
}
```

### Login

- `POST /api/v1/auth/login`

Body:

```json
{
  "email": "user@example.com",
  "password": "User@123"
}
```
Trả về `access_token`, `refresh_token`, `token_type`, `expires_in`.

Lưu ý:

- `token_type` hiện tại trả về giá trị `Bearer`.
- `expires_in` hiện tại là số phút (minute), không phải giây.

### Refresh Token

- `POST /api/v1/auth/refresh`

Body:

```json
{
  "refresh_token": "..."
}
```

### Logout

- `POST /api/v1/auth/logout`

Body:

```json
{
  "refresh_token": "..."
}
```

## Public

### Landing

- `GET /api/v1/public/landing`
- Tra ve: `highlights`, `categories`, `top_ratings`, `top_favorites`.

## Destinations

### List Destinations

- `GET /api/v1/destinations`

Query params:

- `category_slug` (optional)
- `price_level` (optional)
- `rating_min` (optional)
- `keyword` (optional)
- `sort` (optional)
- `page` (default 1)
- `limit` (default 20, max 100)

### Search Destinations

- `GET /api/v1/destinations/search`

Query params:

- `q` (default empty)
- `category_slug` (optional)
- `price_level` (optional)
- `page` (default 1)
- `limit` (default 20, max 100)

### Destination Detail

- `GET /api/v1/destinations/{destination_id}`
- Tự động tăng `view_count` khi xem chi tiết.

Response detail da bao gom them:
Response detail đã bao gồm thêm:

- `insight`: dữ liệu cho tổng hợp destination.
- `metrics`: số liệu tổng hợp (favorite/rating/view) cập nhật bởi worker.

Mẫu `data`:

```json
{
  "id": 1,
  "name": "My Khe Beach",
  "slug": "my-khe-beach",
  "rating_avg": 4.8,
  "categories": [
    {
      "id": 1,
      "name": "Beach",
      "slug": "beach",
      "descriptions": "..."
    }
  ],
  "insight": {
    "destination_id": 1,
    "human_override": {
      "priority": "high"
    },
    "score_snapshot": {
      "scenery": 95
    },
    "final_data": {
      "score": 92,
      "summary": "Bai bien dep",
      "highlights": ["Canh quan rong"],
      "risks": ["Dong nguoi cuoi tuan"],
      "recommendation": "Nen di buoi sang"
    },
    "updated_at": "2026-04-07T03:28:39"
  },
  "metrics": {
    "destination_id": 1,
    "favorite_count": 42,
    "rating_count": 18,
    "rating_sum": 86,
    "view_count": 128,
    "updated_at": "2026-04-07T03:28:39"
  }
}
```

## Interaction (Can Bearer Token)

Header mau:

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

Body:

```json
{
  "rating_score": 5,
  "comment": "Great"
}
```

### Get My Rating

- `GET /api/v1/me/ratings/{destination_id}`

## Admin (Can Bearer Token + role admin)

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
- `POST /api/v1/admin/destinations/bulk`
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

Body bulk create mẫu:

```json
{
  "destinations": [
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
    },
    {
      "name": "Ba Na Hills",
      "slug": "ba-na-hills",
      "address": "Da Nang",
      "description": "Khu du lich noi tieng",
      "price_level": "high",
      "open_hour": "08:00-22:00",
      "img_url": "https://example.com/bana.jpg",
      "url_map": "https://maps.google.com",
      "lat": 15.9951,
      "lng": 107.9964,
      "status": "active",
      "category_ids": [1]
    }
  ]
}
```

Lưu ý bulk create:

- Duplicate slug trong payload -> `VALIDATION_ERROR` (400).
- Slug đã tồn tại trong DB -> `CONFLICT` (409).
- Category ids được validate trước khi tạo destination.

### Admin Stats

- `GET /api/v1/admin/stats/top-favorites`
- `GET /api/v1/admin/stats/top-ratings`
- `GET /api/v1/admin/stats/top-views`

## Analytics

### Summary

- `GET /api/v1/analytics/summary`

### Top Favorites

- `GET /api/v1/analytics/top-favorites?limit=10`

### Top Ratings

- `GET /api/v1/analytics/top-ratings?limit=10`

### Top Views

- `GET /api/v1/analytics/top-views?limit=10`

## Swagger / OpenAPI

API docs portal (gateway):

- `http://localhost:8080/api-docs`

Raw OpenAPI specs:

- `http://localhost:8080/api-docs/specs/auth.json`
- `http://localhost:8080/api-docs/specs/destination.json`
- `http://localhost:8080/api-docs/specs/interaction.json`
- `http://localhost:8080/api-docs/specs/admin.json`
- `http://localhost:8080/api-docs/specs/analytics.json`

Service-scoped Swagger UI:

- `http://localhost:8080/api-docs/swagger/auth`
- `http://localhost:8080/api-docs/swagger/destination`
- `http://localhost:8080/api-docs/swagger/interaction`
- `http://localhost:8080/api-docs/swagger/admin`
- `http://localhost:8080/api-docs/swagger/analytics`

Service-scoped Redoc:

- `http://localhost:8080/api-docs/redoc/auth`
- `http://localhost:8080/api-docs/redoc/destination`
- `http://localhost:8080/api-docs/redoc/interaction`
- `http://localhost:8080/api-docs/redoc/admin`
- `http://localhost:8080/api-docs/redoc/analytics`

Lưu ý quan trọng:

- Trong docker-compose đầy đủ (gateway + frontend), route non-API (`/`) được gateway map về trang thông báo gateway đã hoạt động.
- Vì vậy `http://localhost:8080/docs` và `http://localhost:8080/openapi.json` không phải điểm truy cập docs mặc định.
