# Backend Architecture Notes

## Tổng quan

Backend sử dụng FastAPI theo 2 mode:

- Monolith mode: `app/main.py` mount toàn bộ routers.
- Service-split mode: tách theo domain và đi qua Nginx gateway.

Service backend hiện tại:

- `auth-service`
- `destination-service`
- `interaction-service`
- `admin-service`
- `analytics-service`
- `worker-service` (Kafka consumer, không expose HTTP)

## Thành phần chính

- API layer: `app/routers/*`
- Business layer: `app/services/*`
- Data access layer: `app/repositories/*`
- Persistence: PostgreSQL + SQLAlchemy + Alembic
- Cache + rate-limit: Redis
- Event bus: Kafka
- Search index: Elasticsearch
- Gateway: Nginx ở root repo (`nginx.conf`)

## HTTP Request Flow

1. Request đi vào Nginx gateway.
2. Gateway route theo prefix `/api/v1/*` về service tương ứng.
3. FastAPI middleware tạo `request_id`.
4. Rate-limit theo IP/user được kiểm tra từ Redis.
5. Router xử lý request và gọi service/repository.
6. Response trả về theo chuẩn `response_success` / `response_error`.
7. Header `X-Request-Id` được gắn để trace log xuyên lớp.

## API Prefix và Router

Tất cả routers mount với:

- `settings.api_prefix = /api/v1`

Router groups:

- `/auth`
- `/public`
- `/destinations`
- `/me`
- `/admin`
- `/analytics`

Ngoài prefix API:

- `GET /health`

## Gateway Routing (Docker Compose)

Nginx route map:

- `/api/v1/auth/*` -> `auth-service`
- `/api/v1/public/*` -> `destination-service`
- `/api/v1/destinations/*` -> `destination-service`
- `/api/v1/me/*` -> `interaction-service`
- `/api/v1/admin/*` -> `admin-service`
- `/api/v1/analytics/*` -> `analytics-service`
- `/health` -> `destination-service/health`
- Non-API routes (`/`) -> `frontend:8001`

## Event-driven Analytics Flow

Sự kiện được publish từ routers:

- Favorite create/delete
- Rating upsert
- Destination create/update/delete
- Destination viewed

`worker-service` consume Kafka topics, áp retry theo:

- `WORKER_RETRY_MAX`
- `WORKER_RETRY_BACKOFF_SECONDS`

Khi xử lý thất bại sau retry, event được đẩy sang `KAFKA_DLQ_TOPIC`.

## Security và kiểm soát truy cập

- JWT access/refresh token cho auth.
- `/me/*` yêu cầu access token hợp lệ.
- `/admin/*` yêu cầu role admin.
- Rate-limit:
  - theo IP: `RATE_LIMIT_IP_PER_MIN`
  - theo user: `RATE_LIMIT_USER_PER_MIN`
- Audit logging cho auth/admin actions qua `app.core.audit` và bảng `audit_logs`.

## Caching

Redis được dùng để cache:

- Public landing data
- Destination list/detail
- Admin stats

Khi mutate dữ liệu admin (categories/destinations), cache liên quan được invalidate.

## Data và migration

- Alembic quản lý schema migration.
- `scripts/seed.py` tạo dữ liệu mẫu local.
- Tài khoản seed mặc định:
  - `admin@alats.vn / Admin@123`
  - `user@alats.vn / User@123`

## Vận hành

- Local backend-only: uvicorn + PostgreSQL/Redis cục bộ.
- Full compose: postgres, redis, kafka, elasticsearch, migrate job, 5 API services, worker, frontend, gateway.
- Health endpoint: `GET /health`.
