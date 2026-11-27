# 02 - API Design (REST `/api/v1`)

## 1. API principles

- Base path: `/api/v1`
- Response JSON thống nhất: `success`, `data`, `meta`, `error`
- HTTP method chuẩn: GET/POST/PUT/PATCH/DELETE
- JWT Bearer cho endpoint yêu cầu auth
- Versioning qua URL prefix

## 2. Response contract

### 2.1 Success
```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-03-26T10:00:00Z"
  }
}
```

### 2.2 Error
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": []
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-03-26T10:00:00Z"
  }
}
```

## 3. Auth API

### 3.1 Register
- `POST /api/v1/auth/register`
- Body:
```json
{
  "name": "string",
  "email": "user@example.com",
  "password": "string"
}
```

### 3.2 Login
- `POST /api/v1/auth/login`
- Body:
```json
{
  "email": "user@example.com",
  "password": "string"
}
```
- Response data:
```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 3.3 Refresh token
- `POST /api/v1/auth/refresh`

### 3.4 Logout / revoke
- `POST /api/v1/auth/logout`

## 4. Public Destination API

### 4.1 Landing highlights
- `GET /api/v1/public/landing`
- Dữ liệu: điểm đến nổi bật, category nổi bật, top rating/favorite.

### 4.2 List destinations
- `GET /api/v1/destinations`
- Query:
  - `category_slug`
  - `price_level` (free/low/medium/high)
  - `rating_min`
  - `keyword`
  - `page`, `limit`, `sort`

### 4.3 Destination detail
- `GET /api/v1/destinations/{destination_id}`

### 4.4 Search (Elasticsearch)
- `GET /api/v1/destinations/search`
- Query: `q`, `category_slug`, `price_level`, `page`, `limit`

### 4.5 Activity recommendations (theo code hiện tại)
- `GET /api/v1/public/activities/{activity_slug}/recommendations`
- Query: `page` (default 1), `limit` (default 10, max 100), `budget_level` (tùy chọn)
- Response: `{activity, highlight_destinations, recommended_destinations, trending, error_info}`
- Khi engine lỗi: trả fallback rỗng + mã lỗi nghiệp vụ `ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR`
- Feature flag backend: `ACTIVITY_RECOMMENDATION_ENDPOINT_ENABLED`,
  `FEATURE_ACTIVITY_RECOMMENDATION_*`

## 5. User Interaction API

### 5.1 Favorite destination
- `POST /api/v1/me/favorites/{destination_id}`
- Hành vi idempotent: gọi lặp không tạo record duplicate.

### 5.2 Unfavorite destination
- `DELETE /api/v1/me/favorites/{destination_id}`

### 5.3 List my favorites
- `GET /api/v1/me/favorites`

### 5.4 Create or update rating
- `PUT /api/v1/me/ratings/{destination_id}`
- Body:
```json
{
  "rating_score": 4,
  "comment": "string"
}
```

### 5.5 Get my rating for destination
- `GET /api/v1/me/ratings/{destination_id}`

## 6. Admin API

### 6.1 User management
- `GET /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{id}/status`
- `PATCH /api/v1/admin/users/{id}/role`

### 6.2 Category management
- `GET /api/v1/admin/categories`
- `POST /api/v1/admin/categories`
- `PUT /api/v1/admin/categories/{id}`
- `DELETE /api/v1/admin/categories/{id}`

### 6.3 Destination management
- `GET /api/v1/admin/destinations`
- `POST /api/v1/admin/destinations`
- `POST /api/v1/admin/destinations/bulk` — tạo nhiều destination một lần;
  duplicate slug trong payload → `400 VALIDATION_ERROR`;
  slug đã tồn tại trong DB → `409 CONFLICT`;
  `price` dạng string được giữ ở `price_raw_text`;
  cho phép đồng thời `category_ids` + `category` (tên, fuzzy không dấu/hoa-thường, tự tạo mới);
  `reviews [{rating, text}]` chỉ tính vào insight, không lưu bảng `ratings`
- `PUT /api/v1/admin/destinations/{id}`
- `DELETE /api/v1/admin/destinations/{id}`

### 6.4 Dashboard stats
- `GET /api/v1/admin/stats/top-favorites`
- `GET /api/v1/admin/stats/top-ratings`
- `GET /api/v1/admin/stats/top-views`

## 6.5 Analytics API (theo code hiện tại, public — không yêu cầu auth)
- `GET /api/v1/analytics/summary`
- `GET /api/v1/analytics/top-favorites?limit=10`
- `GET /api/v1/analytics/top-ratings?limit=10`
- `GET /api/v1/analytics/top-views?limit=10`

## 6.6 Internal API (service-to-service, theo code hiện tại — không qua gateway)
- `GET /api/v1/internal/destinations/{id}/active` (no-auth, internal trust)
- `POST /api/v1/internal/destinations/batch` (body `{ids}` — no-auth)
- `POST /api/v1/internal/destinations/{id}/apply-rating-insight` (no-auth)
- `POST /api/v1/internal/destinations/{id}/recompute-rating-avg` (no-auth)
- `GET /api/v1/internal/admin/users`, `PATCH /api/v1/internal/admin/users/{id}/status|role` (yêu cầu admin JWT)
- `GET|POST /api/v1/internal/admin/categories`, `PUT|DELETE /api/v1/internal/admin/categories/{id}` (yêu cầu admin JWT)
- `GET|POST /api/v1/internal/admin/destinations`, `POST /api/v1/internal/admin/destinations/bulk`,
  `PUT|DELETE /api/v1/internal/admin/destinations/{id}` (yêu cầu admin JWT)

## 7. HTTP status code policy

- `200` OK
- `201` Created
- `204` No Content
- `400` Validation
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found
- `409` Conflict
- `429` Too Many Requests
- `500` Internal Error

## 8. Security headers và middleware

- CORS whitelist theo env
- Rate limiting theo IP + user id
- Security headers: HSTS, X-Content-Type-Options, X-Frame-Options
- Input validation với Pydantic

## 9. OpenAPI và automation

- Mỗi service FastAPI expose OpenAPI JSON.
- API Gateway có docs tổng hợp route công khai nội bộ.
- CI quality gate:
  - Validate OpenAPI schema
  - Contract test cho endpoint critical
