# Travel Project

Hệ thống gợi ý và quản trị điểm đến du lịch theo kiến trúc FastAPI microservices + API Gateway.

## Mục tiêu tài liệu

README này là entrypoint cho toàn bộ dự án, dành cho:
- Dev mới onboard nhanh
- Dev backend/frontend cần chạy local
- Reviewer cần nắm kiến trúc và route map

## Cấu trúc chính

- `backend/`: FastAPI app, migrations Alembic, seed data, test
- `frontend/`: mã client (đang ở trạng thái khởi tạo)
- `docker-compose.yml`: môi trường local gồm Postgres, Redis, services, Nginx gateway
- `nginx.conf`: route map từ gateway sang từng service
- `design-docs/`: bộ tài liệu thiết kế (kiến trúc, API, DB, workflow, bảo mật...)

## Kiến trúc runtime (local)

- `postgres` (PostgreSQL 16)
- `redis` (cache + rate limit)
- `migrate` (chạy `alembic upgrade head` + `python scripts/seed.py`)
- `auth-service`
- `destination-service`
- `interaction-service`
- `admin-service`
- `api-gateway` (Nginx, cổng `http://localhost:8080`)

## Quick start

Yêu cầu:
- Docker + Docker Compose

Chạy toàn hệ thống:

```bash
docker compose up --build
```

Kiểm tra gateway:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

Dừng hệ thống:

```bash
docker compose down
```

## API Gateway route map

- `/api/v1/auth/*` -> `auth-service`
- `/api/v1/public/*` -> `destination-service`
- `/api/v1/destinations/*` -> `destination-service`
- `/api/v1/me/*` -> `interaction-service`
- `/api/v1/admin/*` -> `admin-service`

Chi tiết endpoint xem trong `design-docs/02-api-design.md` và README backend.

## Tài liệu liên quan

- Backend setup và vận hành: `backend/README.md`
- Frontend status và kế hoạch: `frontend/README.md`
- Thiết kế hệ thống: `design-docs/README.md`

## Giả định và giới hạn hiện tại

- Frontend chưa có hướng dẫn chạy chi tiết (chưa scaffold rõ ràng).
- Seed mặc định tạo tài khoản mẫu để test local (không dùng cho production).
- Giá trị secret mặc định trong compose chỉ phục vụ môi trường dev.

## Follow-up đề xuất

- Bổ sung OpenAPI export/script để đồng bộ tài liệu API tự động.
- Thêm CI check cho docs (markdown lint + link check).
- Hoàn thiện frontend và cập nhật README tương ứng khi có stack cụ thể.