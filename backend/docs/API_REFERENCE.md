# API Reference (Backend)

Tài liệu này mô tả các endpoint chính của backend FastAPI theo trạng thái code hiện tại.

## Base URL

- Local monolith: `http://localhost:8000`
- Gateway (docker-compose): `http://localhost:8080`
- API prefix: `/api/v1`

## Định Dạng Phản Hồi

### Thành Công

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

### Lỗi

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

### Đăng Ký

- `POST /api/v1/auth/register`

Body:

```json
{
  "name": "User",
  "email": "user@example.com",
  "password": "User@123"
}
```

### Đăng Nhập

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
- `expires_in` hiện tại là số phút, không phải số giây.

### Làm Mới Token

- `POST /api/v1/auth/refresh`

Body:

```json
{
  "refresh_token": "..."
}
```

### Đăng Xuất

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

Trả về: `highlights`, `categories`, `top_ratings`, `top_favorites`.

## Destinations

### Danh Sách Destinations

- `GET /api/v1/destinations`

Query params:

- `category_slug` (tuỳ chọn)
- `price_level` (tuỳ chọn)
- `rating_min` (tuỳ chọn)
- `keyword` (tuỳ chọn)
- `sort` (tuỳ chọn)
- `page` (mặc định 1)
- `limit` (mặc định 20, tối đa 100)

### Tìm Kiếm Destinations

- `GET /api/v1/destinations/search`

Query params:

- `q` (mặc định rỗng)
- `category_slug` (tuỳ chọn)
- `price_level` (tuỳ chọn)
- `page` (mặc định 1)
- `limit` (mặc định 20, tối đa 100)

### Chi Tiết Destination

- `GET /api/v1/destinations/{destination_id}`

- Tự động tăng `view_count` khi xem chi tiết.
- Response chi tiết bao gồm thêm `insight` và `metrics`.

`insight` được khởi tạo khi tạo destination và được cập nhật khi có rating mới hoặc khi bulk create nhận trường `reviews`.

`final_data` bao gồm thêm trường `status` với các giá trị `insufficient_data`, `low_confidence`, `reliable`.

Chi tiết thuật toán và quy tắc xử lý insight xem tại `docs/INSIGHT_PROCESSING.md`.

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
      "summary": "Bãi biển đẹp",
      "highlights": ["Cảnh quan rộng"],
      "risks": ["Đông người cuối tuần"],
      "recommendation": "Nên đi buổi sáng",
      "status": "reliable"
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

## Interaction (cần Bearer Token)

Header mẫu:

```http
Authorization: Bearer <access_token>
```

### Yêu Thích Destination

- `POST /api/v1/me/favorites/{destination_id}`

### Bỏ Yêu Thích Destination

- `DELETE /api/v1/me/favorites/{destination_id}`

### Danh Sách Yêu Thích

- `GET /api/v1/me/favorites`
- Query params: `page`, `limit`

### Cập Nhật Rating

- `PUT /api/v1/me/ratings/{destination_id}`

Body:

```json
{
  "rating_score": 5,
  "comment": "Great"
}
```

### Lấy Rating Của Tôi

- `GET /api/v1/me/ratings/{destination_id}`

## Admin (cần Bearer Token + role admin)

### Users

- `GET /api/v1/admin/users?page=1&limit=20`
- `PATCH /api/v1/admin/users/{user_id}/status`
- `PATCH /api/v1/admin/users/{user_id}/role`

Body cập nhật status:

```json
{
  "status": "active"
}
```

Body cập nhật role:

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

Body tạo/cập nhật:

```json
{
  "name": "Ẩm thực",
  "slug": "food",
  "descriptions": "Quán ăn"
}
```

### Destinations

- `GET /api/v1/admin/destinations?status=active&page=1&limit=20`
- `POST /api/v1/admin/destinations`
- `POST /api/v1/admin/destinations/bulk`
- `PUT /api/v1/admin/destinations/{destination_id}`
- `DELETE /api/v1/admin/destinations/{destination_id}`

Body tạo mẫu:

```json
{
  "name": "My Khe Beach",
  "slug": "my-khe-beach",
  "address": "Vo Nguyen Giap, Da Nang",
  "description": "Bãi biển nổi tiếng",
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
      "description": "Bãi biển nổi tiếng",
      "price": "333.920 ₫",
      "open_hour": "All day",
      "image": ["https://example.com/mykhe.jpg"],
      "maps_url": "https://maps.google.com",
      "lat": 16.0595,
      "lng": 108.2466,
      "status": "active",
      "category_ids": [1, 2],
      "category": ["Điểm thu hút khách du lịch", "Bảo tàng"],
      "reviews": [
        {"rating": 5, "text": "Phong cảnh đẹp, giá hợp lý"},
        {"rating": 4, "text": "Hơi đông nhưng đi lại thuận tiện"}
      ]
    },
    {
      "name": "Ba Na Hills",
      "slug": "ba-na-hills",
      "address": "Da Nang",
      "description": "Khu du lịch nổi tiếng",
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

- Duplicate slug trong payload sẽ trả `VALIDATION_ERROR` (400).
- Slug đã tồn tại trong DB sẽ trả `CONFLICT` (409).
- `price` dạng string sẽ được map sang `price_raw_text`.
- Có thể gửi đồng thời `category_ids` và `category` (danh sách tên category).
- Với `category`: hệ thống tìm category theo tên tương tự (không phân biệt hoa thường/dấu tiếng Việt). Nếu chưa có sẽ tự tạo mới rồi gắn vào destination.
- `reviews` chỉ dùng để tính `insight` cho destination, không lưu vào bảng ratings.

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
