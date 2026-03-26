# Backend (FastAPI)

Backend triển khai theo mô hình module/service với FastAPI, SQLAlchemy, Alembic, Redis cache/rate-limit.

## Đối tượng đọc

- Backend developer
- QA cần test API local
- DevOps cần nắm biến môi trường và luồng chạy

## Cấu trúc chính

- `app/main.py`: app tổng hợp toàn bộ router (monolith mode)
- `app/apps/*.py`: app tách theo service (auth, destination, interaction, admin)
- `app/routers/`: định nghĩa endpoint theo domain
- `app/services/`, `app/repositories/`: business logic và data access
- `app/db/`: models, session, base
- `alembic/`: migration scripts
- `scripts/seed.py`: dữ liệu mẫu local
- `tests/`: test backend

## Biến môi trường

Sao chép từ mẫu:

```bash
cp .env.example .env
```

Các biến chính:
- `DATABASE_URL`
- `JWT_SECRET`, `JWT_ISSUER`, `JWT_ACCESS_TTL_MIN`, `JWT_REFRESH_TTL_DAYS`
- `CORS_ORIGINS`
- `REDIS_URL`
- `CACHE_TTL_SECONDS`
- `RATE_LIMIT_IP_PER_MIN`, `RATE_LIMIT_USER_PER_MIN`

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

Base API: `/api/v1`

## Chạy theo service (không gateway)

```bash
uvicorn app.apps.auth_service:app --reload --port 8001
uvicorn app.apps.destination_service:app --reload --port 8002
uvicorn app.apps.interaction_service:app --reload --port 8003
uvicorn app.apps.admin_service:app --reload --port 8004
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

## Kiểm tra nhanh

Health check:

```bash
curl http://localhost:8080/health
```

Chạy test backend:

```bash
pytest -q
```

## Ghi chú bảo mật và vận hành

- Không dùng `JWT_SECRET=change-me` ngoài môi trường dev.
- Tài khoản mẫu do `scripts/seed.py` tạo chỉ dành cho local/testing.
- Tránh đưa thông tin nhạy cảm (secrets, internal URL) vào tài liệu public.

## Gaps / Follow-up

- Bổ sung tài liệu endpoint chi tiết từ OpenAPI (auto-generated).
- Bổ sung test coverage ngoài `test_health.py` (auth, destinations, interaction, admin).
- Chuẩn hóa lệnh cross-platform (`cp` vs PowerShell) nếu team chủ yếu dùng Windows.
# Login via gateway
curl -X POST http://localhost:8080/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"user@alats.vn","password":"User@123"}'

# Public list
curl http://localhost:8080/api/v1/destinations?page=1&limit=5

# Favorite (replace token)
curl -X POST http://localhost:8080/api/v1/me/favorites/1 -H "Authorization: Bearer <token>"
```

## Tests

```bash
pytest -q
```
