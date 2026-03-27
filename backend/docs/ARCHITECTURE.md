# Backend Architecture Notes

## Tổng quan

Backend dùng FastAPI với 2 mode chạy:

- Monolith mode: một process gồm toàn bộ router (`app/main.py`).
- Service-split mode: tách auth/destination/interaction/admin thành các app riêng (`app/apps/*.py`) và đi qua Nginx gateway.

## Thành phần chính

- API layer: `app/routers/*`
- Business layer: `app/services/*`
- Data access layer: `app/repositories/*`
- Persistence: PostgreSQL + SQLAlchemy + Alembic
- Cache / rate-limit: Redis
- Gateway: Nginx (ở root repo)

## Request Flow

1. Request vào FastAPI app.
2. Middleware tạo `request_id`.
3. Middleware kiểm tra rate-limit theo IP và theo user (nếu có access token hợp lệ).
4. Router xử lý request, gọi service/repository.
5. Trả response theo chuẩn `response_success` / `response_error`.
6. Header trả về có `X-Request-Id` để trace log.

## API Prefix và Router

Toàn bộ router được mount với prefix từ config:

- `settings.api_prefix = /api/v1`

Router groups:

- `/auth`
- `/public`
- `/destinations`
- `/me`
- `/admin`

Ngoài prefix API:

- `GET /health` (không nằm trong `/api/v1`)

## Gateway Routing (docker-compose)

Nginx route map:

- `/api/v1/auth/*` -> `auth-service`
- `/api/v1/public/*` -> `destination-service`
- `/api/v1/destinations/*` -> `destination-service`
- `/api/v1/me/*` -> `interaction-service`
- `/api/v1/admin/*` -> `admin-service`
- `/health` -> `destination-service/health`

## Security và kiểm soát truy cập

- JWT access/refresh token cho auth.
- Endpoint `/me/*` yêu cầu access token hợp lệ.
- Endpoint `/admin/*` yêu cầu role admin.
- Rate-limit:
  - theo IP: `RATE_LIMIT_IP_PER_MIN`
  - theo user: `RATE_LIMIT_USER_PER_MIN`

## Caching

Redis được dùng để cache:

- Public landing data.
- Destination listing/detail.
- Admin stats top views/ratings/favorites.

Khi mutate dữ liệu admin (categories/destinations), cache liên quan được invalidate.

## Data và migration

- Alembic quản lý schema migration.
- Script `scripts/seed.py` tạo dữ liệu mẫu local (admin/user/categories/destinations).
- Tài khoản seed mặc định:
  - `admin@alats.vn / Admin@123`
  - `user@alats.vn / User@123`

## Vận hành

- Local run: uvicorn + PostgreSQL + Redis cục bộ.
- Compose run: gồm postgres, redis, migrate job, 4 services, api-gateway.
- Health endpoint để kiểm tra liveness nhanh.
