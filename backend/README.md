# Backend (FastAPI)

Backend là lớp nghiệp vụ chính của Travel Project, cung cấp API theo domain và phát event cho worker xử lý analytics/search.

Cập nhật: 2026-04-24

## 1. Vai trò backend

- Quản lý auth và phiên đăng nhập token.
- Cung cấp destinations/public feed/chi tiết.
- Xử lý favorites, ratings và admin operations.
- Tính toán metrics và insight cho destination.
- Publish event sang Kafka cho worker.

## 2. Architecture map

- Monolith mode: `uvicorn app.main:app --reload`.
- Service-split mode: auth, destination, interaction, admin, analytics qua API gateway.
- Worker mode: `app.worker.consumer`.

Folder quan trọng:

- `app/routers`: API endpoints.
- `app/services`: business logic.
- `app/repositories`: data access.
- `app/db`: models + session.
- `app/worker`: kafka consumer.
- `alembic`: migrations.
- `scripts`: seed, replay DLQ, backfill image.
- `tests`: backend tests.

## 3. Tài liệu backend

- `docs/README.md`
- `docs/API_REFERENCE.md`
- `docs/ARCHITECTURE.md`
- `docs/INSIGHT_PROCESSING.md`
- `docs/SECURITY_RUNBOOK.md`
- `docs/WORKER_RUNBOOK.md`
- `docs/OBSERVABILITY_BASELINE.md`
- `docs/DEPLOYMENT_RUNBOOK.md`

## 4. Biến môi trường

Tạo file env từ mẫu:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Nhóm biến chính:

- Data source và pools: `DATABASE_URL`, `DB_POOL_*`
- Auth và security: `JWT_*`, `CORS_ORIGINS`
- Cache và rate-limit: `REDIS_*`, `CACHE_TTL_SECONDS`, `RATE_LIMIT_*`
- Event pipeline: `KAFKA_*`
- Search: `ELASTICSEARCH_*`, `SEARCH_USE_ELASTICSEARCH`
- Worker reliability: `WORKER_RETRY_*`
- Destination images: `DESTINATION_IMAGE_*`, `CLOUDINARY_*`

Lưu ý:

- `JWT_SECRET` tối thiểu 32 ký tự.
- `CORS_ORIGINS` phải là whitelist cụ thể.

## 5. Chạy backend local (không Docker)

1) Cài dependencies

```bash
pip install -r requirements.txt
```

2) Chạy migration

```bash
alembic upgrade head
```

3) Seed data

```bash
python scripts/seed.py
```

4) Chạy API app

```bash
uvicorn app.main:app --reload
```

5) Chạy worker (tùy chọn)

```bash
python -m app.worker.consumer
```

6) Replay DLQ (tùy chọn)

```bash
python scripts/replay_dlq.py --limit 100
```

7) Backfill image Cloudinary (tùy chọn)

```bash
python scripts/backfill_destination_images.py --batch-size 50
```

## 6. Chạy full stack bằng Docker Compose

Từ root project:

```bash
docker compose up --build
```

Sau khi lên:

- Gateway: http://localhost:8080
- Docs portal: http://localhost:8080/api-docs
- Frontend (service riêng): http://localhost

## 7. Kiểm tra nhanh

Health:

```bash
curl http://localhost:8080/health
```

Login:

```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@alats.vn","password":"User@123"}'
```

Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"user@alats.vn","password":"User@123"}'
```

Docs URLs:

- http://localhost:8080/api-docs
- http://localhost:8080/api-docs/specs/admin.json
- http://localhost:8080/api-docs/swagger/admin
- http://localhost:8080/api-docs/redoc/admin

## 8. Test

Chạy test nhanh:

```bash
pytest -q
```

Chạy với coverage gate:

```bash
pytest tests -q --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=70
```

## 9. Tài khoản seed

- Admin: `admin@alats.vn / Admin@123`
- User: `user@alats.vn / User@123`

Chỉ dùng cho local và test.

## 10. Vận hành và bảo mật

- Không sử dụng secret mặc định ngoài môi trường dev.
- Không đưa secrets vào codebase.
- Khi thay đổi route map hoặc backend image trong compose, cần rebuild + force recreate để tránh runtime stale.
