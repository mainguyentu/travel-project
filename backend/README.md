# Backend (FastAPI)

Backend triển khai theo mô hình module/service với FastAPI, SQLAlchemy, Alembic và Redis (cache + rate-limit).

Backend là phần lõi nghiệp vụ của Travel Project, đồng thời publish events sang Kafka để worker cập nhật analytics và search index.

## Mục tiêu tài liệu

- Backend developer: nắm nhanh cấu trúc và luồng chạy.
- QA: có checklist test API local nhanh.
- DevOps: nắm rõ biến môi trường và mode chạy.

## Cập nhật theo tiến độ hiện tại

- Bổ sung API docs portal tại gateway: `/api-docs`, specs theo từng service và trang Swagger/Redoc riêng.
- Bổ sung endpoint admin bulk create destinations: `POST /api/v1/admin/destinations/bulk`.
- Payload destination detail đã bao gồm thêm `insight` và `metrics`.

## Tài liệu liên quan trong backend

- `docs/API_REFERENCE.md`: danh sách endpoint và payload mẫu.
- `docs/ARCHITECTURE.md`: kiến trúc runtime, data flow, gateway route map.
- `docs/INSIGHT_PROCESSING.md`: thuật toán và quy tắc cập nhật insight theo rating/comment.
- `docs/SECURITY_RUNBOOK.md`: quy trình bảo mật, rotation secrets, incident checklist.
- `docs/WORKER_RUNBOOK.md`: vận hành worker, DLQ và replay.
- `docs/OBSERVABILITY_BASELINE.md`: guardrails DB/Redis và threshold cảnh báo.
- `docs/DEPLOYMENT_RUNBOOK.md`: quy trình release/deploy staging/production qua GitHub Actions.
- `../DOCKER_INTEGRATION.md`: tổng quan tích hợp Docker toàn hệ thống.

## Cấu trúc chính

- `app/main.py`: app tổng hợp toàn bộ router (monolith mode, chạy bằng `uvicorn app.main:app`).
- `app/apps/*.py`: app tách theo service (auth, destination, interaction, admin, analytics).
- `app/routers/`: endpoint theo domain.
- `app/services/`, `app/repositories/`: business logic và data access.
- `app/services/insight.py`: xử lý insight theo luồng tạo destination và cập nhật rating.
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
- `DESTINATION_IMAGE_CLOUDINARY_ENABLED`
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `CLOUDINARY_UPLOAD_FOLDER`
- `DESTINATION_IMAGE_TIMEOUT_SECONDS`, `DESTINATION_IMAGE_MAX_BYTES`, `DESTINATION_IMAGE_UPLOAD_CONCURRENCY`
- `DESTINATION_IMAGE_BACKFILL_BATCH_SIZE`, `DESTINATION_IMAGE_BACKFILL_SLEEP_SECONDS`, `DESTINATION_IMAGE_BACKFILL_CHECKPOINT_FILE`

Lưu ý bảo mật cấu hình:

- `JWT_SECRET` bắt buộc tối thiểu 32 ký tự.
- `CORS_ORIGINS` bắt buộc là whitelist origin cụ thể (không cho phép `*`).
- `CORS_ORIGINS` hỗ trợ định dạng JSON array hoặc chuỗi ngăn cách dấu phẩy.

## Chạy local (không Docker)

1. Cài dependencies

```bash
pip install -r requirements.txt
```

2. Chạy migration

```bash
alembic upgrade head
```

3. Seed dữ liệu mẫu

```bash
python scripts/seed.py
```

4. Chạy app tổng hợp

```bash
uvicorn app.main:app --reload
```

Mặc định app chạy ở `http://localhost:8000`.

- Health: `GET /health`
- API prefix: `/api/v1`
- Swagger UI: `/docs`

5. (Tuỳ chọn) chạy worker local

```bash
python -m app.worker.consumer
```

Replay event từ DLQ:

```bash
python scripts/replay_dlq.py --limit 100
```

Backfill ảnh destination lên Cloudinary (batch + checkpoint/resume):

```bash
python scripts/backfill_destination_images.py --batch-size 50
```

Ví dụ chạy thử giới hạn 2 batch đầu:

```bash
python scripts/backfill_destination_images.py --batch-size 50 --max-batches 2
```

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

Frontend khi chạy full Docker Compose ở `http://localhost` (service `frontend`, cổng host 80).

Gateway chỉ phục vụ API và docs portal; root `/` trả về trạng thái gateway, không proxy frontend.

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

Lưu ý: cần bật Kafka/Elasticsearch theo biến môi trường (`KAFKA_ENABLED`, `ELASTICSEARCH_ENABLED`) hoặc chạy qua Docker Compose.

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

API docs nhanh:

```text
http://localhost:8080/api-docs
http://localhost:8080/api-docs/specs/admin.json
http://localhost:8080/api-docs/swagger/admin
http://localhost:8080/api-docs/redoc/admin
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

Chạy test có coverage gate (tương đương CI quality workflow):

```bash
pytest tests -q --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=70
```

## Tài khoản seed mặc định (local)

- Admin: `admin@alats.vn / Admin@123`
- User: `user@alats.vn / User@123`

## Ghi chú bảo mật và vận hành

- Không dùng `JWT_SECRET=change-me` ngoài môi trường dev.
- Tài khoản mẫu từ `scripts/seed.py` chỉ dùng cho local/testing.
- Tránh đưa secrets hoặc internal URL vào tài liệu public.
- Khi deploy staging/production, tham chiếu `docs/DEPLOYMENT_RUNBOOK.md` để cấu hình secrets/workflows đúng chuẩn.
- Khi backend code hoặc route map thay đổi trong Docker, rebuild và force recreate các backend services cùng `api-gateway` để tránh container dùng image hoặc upstream cũ.
