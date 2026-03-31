# Travel Project

Hệ thống gợi ý và quản trị điểm đến du lịch, gồm:

- Backend FastAPI (service split qua API Gateway)
- Frontend Laravel Blade (SSR) gọi API qua gateway
- Hạ tầng local bằng Docker Compose (PostgreSQL, Redis, Kafka, Elasticsearch, Nginx)

README này là tài liệu tổng (entrypoint) để onboard nhanh toàn dự án.

## 1. Cấu trúc workspace

- `backend/`: FastAPI app, Alembic migration, seed script, test.
- `frontend/`: Laravel UI (public + user + admin), gọi API backend.
- `docker-compose.yml`: stack local đầy đủ.
- `nginx.conf`: route map gateway tới từng backend service.
- `design-docs/`: bộ tài liệu phân tích thiết kế và chuẩn triển khai.

## 2. Kiến trúc runtime (local)

Các container chính:

- `postgres` (PostgreSQL 16)
- `redis`
- `kafka`
- `elasticsearch`
- `migrate` (chạy migration + seed)
- `auth-service`
- `destination-service`
- `interaction-service`
- `admin-service`
- `analytics-service`
- `worker-service`
- `api-gateway` (Nginx, `http://localhost:8080`)

Gateway route map:

- `/api/v1/auth/*` -> `auth-service`
- `/api/v1/public/*` -> `destination-service`
- `/api/v1/destinations/*` -> `destination-service`
- `/api/v1/me/*` -> `interaction-service`
- `/api/v1/admin/*` -> `admin-service`
- `/api/v1/analytics/*` -> `analytics-service`

## 3. Quick Start (khuyến nghị)

Yêu cầu:

- Docker + Docker Compose

Chạy toàn hệ thống:

```bash
docker compose up --build
```

PowerShell (Windows):

```powershell
docker compose up --build
```

Kiểm tra nhanh:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

Dừng:

```bash
docker compose down
```

## 4. Chạy tách frontend/backend

### 4.1 Backend

Xem hướng dẫn chi tiết tại `backend/README.md`.

Luồng cơ bản:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

### 4.2 Frontend

Xem hướng dẫn chi tiết tại `frontend/README.md`.

Luồng cơ bản:

```bash
cd frontend
composer install
cp .env.example .env
php artisan key:generate
npm install
php artisan serve
npm run dev
```

Mặc định frontend sẽ gọi API tại `API_BASE_URL=http://localhost:8080`.

## 5. URL và endpoint quan trọng

- Frontend UI: `http://127.0.0.1:8000`
- API Gateway: `http://localhost:8080`
- Health gateway: `GET /health`
- Analytics summary: `GET /api/v1/analytics/summary`
- Swagger backend (monolith mode): `http://localhost:8000/docs`

## 6. Bộ tài liệu chính

- Tổng hợp backend: `backend/README.md`
- API backend: `backend/docs/API_REFERENCE.md`
- Kiến trúc backend: `backend/docs/ARCHITECTURE.md`
- Tổng hợp frontend: `frontend/README.md`
- Bộ design docs: `design-docs/README.md`

## 7. Tài khoản seed local

- Admin: `admin@alats.vn / Admin@123`
- User: `user@alats.vn / User@123`

Chỉ dùng cho môi trường dev/test local.

## 8. Ghi chú vận hành và bảo mật

- Không dùng secret mặc định ở staging/production.
- Không commit thông tin nhạy cảm vào `.env`.
- Gateway và route map là hợp đồng tích hợp giữa frontend và backend.
- Test E2E smoke backend có tại `backend/tests/test_smoke_e2e.py`.

## 9. Troubleshooting nhanh (Windows PowerShell)

- Ưu tiên dùng `curl.exe` thay vì alias `curl` để tránh lỗi tham số.
- Với request JSON, dùng `Invoke-RestMethod` sẽ ổn định hơn cho quoting.

Ví dụ:

```powershell
curl.exe http://localhost:8080/health

Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/auth/login" `
	-ContentType "application/json" `
	-Body '{"email":"user@alats.vn","password":"User@123"}'
```

## 10. Repository-wide quality pipeline (P4)

CI tại root dùng workflow:

- `.github/workflows/repo-quality.yml`

Nội dung chính:

- Backend tests + coverage gate
- Frontend build + feature tests + coverage artifact
- Security scan dependency (pip/composer/npm) + backend image scan (Trivy)

Chạy local một lệnh trên Windows PowerShell:

```powershell
./scripts/ci.ps1
```

Nếu cần bỏ qua security scan (chạy nhanh vòng test/build):

```powershell
./scripts/ci.ps1 -SkipSecurity
```

## 11. CI/CD Product Deployment (P5)

Workflow mới tại root:

- `.github/workflows/release-build.yml`: build + push image backend và API gateway lên GHCR.
- `.github/workflows/deploy-staging.yml`: deploy staging qua SSH, sau đó chạy post-deploy SLO checks.
- `.github/workflows/deploy-production.yml`: deploy production có approval qua GitHub Environment + hỗ trợ rollback theo tag.
- `.github/workflows/post-deploy-slo-check.yml`: reusable workflow kiểm tra health/read/analytics latency sau deploy.
- `.github/workflows/release-notes.yml`: tự động draft release notes bằng Release Drafter.

Tài liệu vận hành:

- `backend/docs/DEPLOYMENT_RUNBOOK.md`

Các secret cần cấu hình được liệt kê đầy đủ trong runbook trên.