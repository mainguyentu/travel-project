# Backend (FastAPI)

Backend triển khai theo mô hình module/service với FastAPI, SQLAlchemy, Alembic và Redis (cache + rate-limit).

## Mục tiêu tài liệu

- Backend developer: nắm nhanh cấu trúc và luồng chạy.
- QA: có checklist test API local nhanh.
- DevOps: nắm rõ biến môi trường và mode chạy.

## Tài liệu liên quan trong backend

- `docs/API_REFERENCE.md`: danh sách endpoint và payload mẫu.
- `docs/ARCHITECTURE.md`: kiến trúc runtime, data flow, gateway route map.

## Cấu trúc chính

- `app/main.py`: app tổng hợp toàn bộ router (monolith mode).
- `app/apps/*.py`: app tách theo service (auth, destination, interaction, admin).
- `app/apps/*.py`: app tách theo service (auth, destination, interaction, admin, analytics).
- `app/routers/`: endpoint theo domain.
- `app/services/`, `app/repositories/`: business logic và data access.
- `app/db/`: models, session, base.
- `app/worker/`: Kafka consumer xử lý analytics/search bất đồng bộ.
- `alembic/`: migration scripts.
- `scripts/seed.py`: dữ liệu mẫu local.
- `tests/`: test backend.

## Biến môi trường

Sao chép từ mẫu:

```bash
cp .env.example .env
```

PowerShell (Windows):

```powershell
Copy-Item .env.example .env
```

Các biến chính:

- `DATABASE_URL`
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`
- `JWT_SECRET`, `JWT_ISSUER`, `JWT_ACCESS_TTL_MIN`, `JWT_REFRESH_TTL_DAYS`
- `CORS_ORIGINS`
- `REDIS_URL`, `REDIS_MAX_CONNECTIONS`, `REDIS_SOCKET_CONNECT_TIMEOUT`, `REDIS_SOCKET_TIMEOUT`
- `CACHE_TTL_SECONDS`
- `RATE_LIMIT_IP_PER_MIN`, `RATE_LIMIT_USER_PER_MIN`
- `KAFKA_ENABLED`, `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC_*`, `KAFKA_DLQ_TOPIC`, `KAFKA_CONSUMER_GROUP`
- `ELASTICSEARCH_ENABLED`, `ELASTICSEARCH_URL`, `ELASTICSEARCH_INDEX`, `SEARCH_USE_ELASTICSEARCH`
- `WORKER_RETRY_MAX`, `WORKER_RETRY_BACKOFF_SECONDS`

Lưu ý bảo mật cấu hình:

- `JWT_SECRET` bắt buộc tối thiểu 32 ký tự.
- `CORS_ORIGINS` bắt buộc là whitelist origin cụ thể (không cho phép `*`).
- `CORS_ORIGINS` hỗ trợ định dạng JSON array hoặc chuỗi ngăn cách dấu phẩy.

## Chạy local (không Docker)

1) Cài dependencies

```bash
pip install -r requirements.txt
```

2) Chạy migration

```bash
alembic upgrade head
```

3) Seed dữ liệu mẫu

```bash
python scripts/seed.py
```

4) Chạy app tổng hợp

```bash
uvicorn app.main:app --reload
```

Mặc định app chạy ở `http://localhost:8000`.

- Health: `GET /health`
- API prefix: `/api/v1`
- Swagger UI: `/docs`

## Chạy theo service (không gateway)

```bash
uvicorn app.apps.auth_service:app --reload --port 8001
uvicorn app.apps.destination_service:app --reload --port 8002
uvicorn app.apps.interaction_service:app --reload --port 8003
uvicorn app.apps.admin_service:app --reload --port 8004
uvicorn app.apps.analytics_service:app --reload --port 8005
```

## Chạy full stack với Docker Compose (khuyến nghị)

Từ thư mục root project:

```bash
docker compose up --build
```

Gateway: `http://localhost:8080`

Route map qua gateway:

- `/api/v1/auth/*` -> `auth-service`
- `/api/v1/public/*` -> `destination-service`
- `/api/v1/destinations/*` -> `destination-service`
- `/api/v1/me/*` -> `interaction-service`
- `/api/v1/admin/*` -> `admin-service`
- `/api/v1/analytics/*` -> `analytics-service`

### Worker service

Consumer xử lý event Kafka (favorite/rating/destination/view):

```bash
python -m app.worker.consumer
```

## Kiểm tra nhanh

Health check:

```bash
curl http://localhost:8080/health
```

PowerShell (Windows):

```powershell
curl.exe http://localhost:8080/health
```

Login qua gateway:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
	-H "Content-Type: application/json" \
	-d '{"email":"user@alats.vn","password":"User@123"}'
```

PowerShell (Windows):

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/auth/login" `
	-ContentType "application/json" `
	-Body '{"email":"user@alats.vn","password":"User@123"}'
```

Public list:

```bash
curl "http://localhost:8080/api/v1/destinations?page=1&limit=5"
```

Favorite (thay `<token>`):

```bash
curl -X POST http://localhost:8080/api/v1/me/favorites/1 \
	-H "Authorization: Bearer <token>"
```

Chạy test backend:

```bash
pytest -q
```

## Tài khoản seed mặc định (local)

- Admin: `admin@alats.vn / Admin@123`
- User: `user@alats.vn / User@123`

## Ghi chú bảo mật và vận hành

- Không dùng `JWT_SECRET=change-me` ngoài môi trường dev.
- Tài khoản mẫu từ `scripts/seed.py` chỉ dùng cho local/testing.
- Tránh đưa secrets hoặc internal URL vào tài liệu public.
