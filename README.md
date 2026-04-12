# Travel Project

Hệ thống gợi ý và quản trị điểm đến du lịch, gồm:

- Backend FastAPI (service split qua API Gateway)
- Frontend Laravel Blade (SSR) gọi API qua gateway
- Hạ tầng local bằng Docker Compose (PostgreSQL, Redis, Kafka, Elasticsearch, Nginx)

README này là tài liệu tổng để onboard nhanh toàn dự án.

## 0. Tổng Quan Dự Án

Travel Project là hệ thống full-stack gồm backend API và frontend SSR, được tổ chức theo kiến trúc service-split qua API Gateway.

Phạm vi chính:

- Quản lý người dùng và xác thực JWT.
- Khám phá điểm đến, yêu thích, đánh giá.
- Quản trị dữ liệu users/categories/destinations.
- Thống kê analytics theo lượt xem/yêu thích/đánh giá.
- Hạ tầng local và deploy bằng Docker Compose + GitHub Actions.

## 0.1 Tiến Độ Hiện Tại (2026-04)

- API docs portal đã hoạt động tại gateway qua `/api-docs` (raw specs + Swagger + Redoc theo từng service).
- Frontend admin UI đã có đầy đủ thao tác ghi dữ liệu cho users, categories, destinations.
- Backend admin đã bổ sung endpoint bulk create destinations.
- Destination detail payload đã bổ sung `insight` và `metrics` cho popup chi tiết frontend.

## 1. Cấu trúc workspace

- `backend/`: FastAPI app, Alembic migration, seed script, test.
- `frontend/`: Laravel UI (public + user + admin), gọi API backend.
- `docker-compose.yml`: stack local đầy đủ.
- `nginx.conf`: route map gateway tới từng backend service.
- `design-docs/`: bộ tài liệu phân tích thiết kế và chuẩn triển khai.
- `DOCKER_INTEGRATION.md`: tài liệu tích hợp Docker runtime và routing gateway.

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

## 3. Bắt Đầu Nhanh (khuyến nghị)

Yêu cầu:

- Docker + Docker Compose

Chạy toàn hệ thống (lần đầu):

```bash
docker compose up --build
```

PowerShell (Windows):

```powershell
docker compose up --build
```

Từ lần sau, khi chỉ thay đổi code nhỏ (không đổi dependency), chạy lại không cần build:

```bash
docker compose up -d
```

```powershell
docker compose up -d
```

Với cấu hình hiện tại, backend API chạy `uvicorn --reload` và source code được bind mount nên thay đổi code sẽ tự áp dụng trong container.

Kiểm tra nhanh:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

PowerShell (Windows):

```powershell
curl.exe http://localhost:8080/
curl.exe http://localhost:8080/health
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

- Frontend UI (Docker gateway): `http://localhost:8080`

- Frontend UI (chạy frontend local tách riêng): `http://127.0.0.1:8000`

- API Gateway: `http://localhost:8080`

- API Docs Portal: `http://localhost:8080/api-docs`

- Health gateway: `GET /health`

- OpenAPI specs:
  - `http://localhost:8080/api-docs/specs/auth.json`

  - `http://localhost:8080/api-docs/specs/destination.json`

  - `http://localhost:8080/api-docs/specs/interaction.json`

  - `http://localhost:8080/api-docs/specs/admin.json`

  - `http://localhost:8080/api-docs/specs/analytics.json`

- Swagger service docs:
  - `http://localhost:8080/api-docs/swagger/auth`

  - `http://localhost:8080/api-docs/swagger/destination`

  - `http://localhost:8080/api-docs/swagger/interaction`

  - `http://localhost:8080/api-docs/swagger/admin`

  - `http://localhost:8080/api-docs/swagger/analytics`

- Redoc service docs:
  - `http://localhost:8080/api-docs/redoc/auth`

  - `http://localhost:8080/api-docs/redoc/destination`

  - `http://localhost:8080/api-docs/redoc/interaction`

  - `http://localhost:8080/api-docs/redoc/admin`

  - `http://localhost:8080/api-docs/redoc/analytics`

- Analytics summary: `GET /api/v1/analytics/summary`

- Swagger backend (monolith mode): `http://localhost:8000/docs`

## 6. Bộ tài liệu chính

- Tổng hợp backend: `backend/README.md`

- API backend: `backend/docs/API_REFERENCE.md`

- Kiến trúc backend: `backend/docs/ARCHITECTURE.md`

- Thuật toán insight destination: `backend/docs/INSIGHT_PROCESSING.md`

- Runbook deploy: `backend/docs/DEPLOYMENT_RUNBOOK.md`

- Runbook bảo mật: `backend/docs/SECURITY_RUNBOOK.md`

- Runbook worker: `backend/docs/WORKER_RUNBOOK.md`

- Baseline quan sát: `backend/docs/OBSERVABILITY_BASELINE.md`

- Tổng hợp frontend: `frontend/README.md`

- Bộ design docs: `design-docs/README.md`

- Docker integration: `DOCKER_INTEGRATION.md`

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

## 10. Pipeline Chất Lượng Toàn Repo (P4)

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

## 11. Triển Khai CI/CD Sản Phẩm (P5)

Workflow mới tại root:

- `.github/workflows/release-build.yml`: build + push image backend và API gateway lên GHCR.

- `.github/workflows/deploy-staging.yml`: deploy staging qua SSH, sau đó chạy post-deploy SLO checks.

- `.github/workflows/deploy-production.yml`: deploy production có approval qua GitHub Environment + hỗ trợ rollback theo tag.

- `.github/workflows/post-deploy-slo-check.yml`: reusable workflow kiểm tra health/read/analytics latency sau deploy.

- `.github/workflows/release-notes.yml`: tự động draft release notes bằng Release Drafter.

Tài liệu vận hành:

- `backend/docs/DEPLOYMENT_RUNBOOK.md`

Các secret cần cấu hình được liệt kê đầy đủ trong runbook trên.
