# Docker Integration: Backend + Frontend

## Overview

Tài liệu này mô tả trạng thái Docker integration mới nhất của dự án.

Hiện tại `docker-compose.yml` chạy đầy đủ:

- Backend FastAPI (auth, destination, interaction, admin, analytics)
- Worker xử lý sự kiện Kafka
- Frontend Laravel
- API Gateway Nginx
- PostgreSQL, Redis, Kafka, Elasticsearch

## Runtime Architecture

```text
User (http://localhost:8080)
    |
    v
Nginx Gateway (api-gateway)
    |- /api/v1/auth/*         -> auth-service:8000
    |- /api/v1/public/*       -> destination-service:8000
    |- /api/v1/destinations/* -> destination-service:8000
    |- /api/v1/me/*           -> interaction-service:8000
    |- /api/v1/admin/*        -> admin-service:8000
    |- /api/v1/analytics/*    -> analytics-service:8000
    |- /api-docs              -> static docs portal
    |- /api-docs/specs/*.json -> per-service openapi.json
    |- /api-docs/swagger/*    -> proxied FastAPI /docs
    |- /api-docs/redoc/*      -> proxied FastAPI /redoc
    |- /health                -> destination-service:8000/health
    '- / (non-API routes)     -> frontend:8001

Background:
    |- postgres:5432
    |- redis:6379
    |- kafka:9092
    '- elasticsearch:9200
```

## Services (Compose Local)

- `postgres`
- `redis`
- `kafka`
- `elasticsearch`
- `migrate` (alembic + seed rồi exit)
- `auth-service`
- `destination-service`
- `interaction-service`
- `admin-service`
- `analytics-service`
- `worker-service`
- `frontend`
- `api-gateway`

## Quick Start

### 1) Build và chạy toàn stack

```bash
docker compose up --build -d
```

### 2) Kiểm tra nhanh

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
curl "http://localhost:8080/api/v1/destinations?page=1&limit=5"
```

### 3) Xem logs

```bash
docker compose logs -f
docker compose logs -f api-gateway
docker compose logs -f frontend
docker compose logs -f worker-service
```

### 4) Dừng stack

```bash
docker compose down
```

## Frontend in Docker

Frontend service build từ `frontend/Dockerfile` và chạy Laravel trên port nội bộ `8001`.

Biến môi trường chính trong local compose:

- `APP_ENV=local`
- `APP_DEBUG=true`
- `APP_URL=http://localhost:8080`
- `API_GATEWAY_URL=http://localhost:8080`

Lưu ý: gateway route non-API về frontend, nên UI được truy cập qua `http://localhost:8080`.
Docs portal được truy cập qua `http://localhost:8080/api-docs`.

## Migrate Job

Service `migrate` chạy tự động trước backend services:

1. `alembic upgrade head`
2. `python scripts/seed.py`

Sau khi hoàn tất, service này exit với trạng thái thành công.

## Deploy Compose (staging/production)

Dành cho deploy từ CI/CD dùng file:

- `docker-compose.deploy.yml`

Image được inject qua env:

- `BACKEND_IMAGE`
- `GATEWAY_IMAGE`

Lệnh chuẩn trên target host:

```bash
docker compose -f docker-compose.deploy.yml pull
docker compose -f docker-compose.deploy.yml up -d --remove-orphans
```

Chi tiết xem runbook: `backend/docs/DEPLOYMENT_RUNBOOK.md`.

## Troubleshooting

### Port 8080 đã bị chiếm

```powershell
netstat -ano | findstr :8080
```

Đổi mapping cổng ở `docker-compose.yml`, ví dụ `8081:80`.

### Gateway route sai

```bash
docker compose logs -f api-gateway
```

Kiểm tra lại `nginx.conf` và restart stack.

### Frontend container unhealthy

```bash
docker compose logs -f frontend
```

Rebuild nếu cần:

```bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Worker xử lý event lỗi

```bash
docker compose logs -f worker-service
```

Nếu DLQ tăng cao, xem `backend/docs/WORKER_RUNBOOK.md`.

## Notes

- Dùng `docker compose` (plugin v2) thay vì `docker-compose` legacy.
- Không đưa secrets production vào `docker-compose.yml`; dùng secret manager/CI secrets.
