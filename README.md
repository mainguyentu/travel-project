# Travel Project

Travel Project là hệ thống full-stack phục vụ quản lý và khám phá điểm đến du lịch, gồm backend API, frontend SSR và hạ tầng local/CI-CD.

README tổng này đóng vai trò:

- Tổng quan kiến trúc và phạm vi dự án.
- Hướng dẫn chạy nhanh cho thành viên mới.
- Bản đồ tài liệu để tra cứu đúng ngữ cảnh.

Cập nhật: 2026-04-24

## 1. Tổng quan dự án

Thành phần chính:

- Backend: FastAPI, SQLAlchemy, Alembic, Redis, Kafka, Elasticsearch.
- Frontend: Laravel Blade SSR + Vite.
- Gateway: Nginx định tuyến API theo service và host docs portal.
- Runtime local: Docker Compose.

Nghiệp vụ chính:

- Xác thực người dùng bằng access token và refresh token.
- Public destinations: tìm kiếm, lọc, xem chi tiết.
- Tương tác người dùng: favorites, ratings.
- Quản trị: users, categories, destinations, stats.
- Analytics và worker xử lý event bất đồng bộ.

## 2. Kiến trúc runtime

Trong Docker Compose:

- Frontend UI: http://localhost
- API Gateway + docs: http://localhost:8080
- Gateway root `/` chỉ trả trạng thái, không proxy frontend.

Service map qua gateway:

- `/api/v1/auth/*` -> auth-service
- `/api/v1/public/*` -> destination-service
- `/api/v1/destinations/*` -> destination-service
- `/api/v1/me/*` -> interaction-service
- `/api/v1/admin/*` -> admin-service
- `/api/v1/analytics/*` -> analytics-service

## 3. Cấu trúc workspace

- `backend/`: backend app, migrations, scripts, tests, backend docs.
- `frontend/`: Laravel UI, SSR pages, API client bridge.
- `design-docs/`: bộ tài liệu thiết kế và implementation plan.
- `docker-compose.yml`: stack local đầy đủ.
- `docker-compose.deploy.yml`: stack deploy.
- `nginx.conf`: gateway routing cho API và docs portal.
- `scripts/ci.ps1`: script quality gate local.

## 4. Chạy nhanh bằng Docker Compose (khuyến nghị)

Yêu cầu:

- Docker Desktop (hoặc Docker Engine + Compose plugin).

Lần đầu:

```bash
docker compose up --build
```

Lần sau:

```bash
docker compose up -d
```

Dừng stack:

```bash
docker compose down
```

Kiểm tra nhanh:

```bash
curl http://localhost:8080/health
```

Windows PowerShell:

```powershell
curl.exe http://localhost:8080/health
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"user@alats.vn","password":"User@123"}'
```

## 5. Chạy tách riêng từng phần

Backend:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
composer install
cp .env.example .env
php artisan key:generate
npm install
php artisan serve
npm run dev
```

Lưu ý:

- Frontend mặc định gọi API qua `API_BASE_URL=http://localhost:8080`.

## 6. URL quan trọng

- Frontend UI (compose): http://localhost
- Frontend UI (local): http://127.0.0.1:8000
- API gateway: http://localhost:8080
- API docs portal: http://localhost:8080/api-docs
- Gateway health: `GET /health`
- Backend monolith swagger (khi chạy backend riêng): http://localhost:8000/docs

OpenAPI specs qua gateway:

- `/api-docs/specs/auth.json`
- `/api-docs/specs/destination.json`
- `/api-docs/specs/interaction.json`
- `/api-docs/specs/admin.json`
- `/api-docs/specs/analytics.json`

## 7. Tài khoản seed local

- Admin: `admin@alats.vn / Admin@123`
- User: `user@alats.vn / User@123`

Chỉ dùng cho local và test.

## 8. Bản đồ tài liệu

Tài liệu tổng quan:

- `backend/README.md`
- `frontend/README.md`
- `design-docs/README.md`
- `DOCKER_INTEGRATION.md`

Tài liệu backend chi tiết:

- `backend/docs/README.md`
- `backend/docs/API_REFERENCE.md`
- `backend/docs/ARCHITECTURE.md`
- `backend/docs/INSIGHT_PROCESSING.md`
- `backend/docs/SECURITY_RUNBOOK.md`
- `backend/docs/WORKER_RUNBOOK.md`
- `backend/docs/OBSERVABILITY_BASELINE.md`
- `backend/docs/DEPLOYMENT_RUNBOOK.md`

## 9. Quality gate và CI/CD

Quality workflow:

- `.github/workflows/repo-quality.yml`
- `scripts/ci.ps1`

Release/deploy workflows:

- `.github/workflows/release-build.yml`
- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`
- `.github/workflows/post-deploy-slo-check.yml`
- `.github/workflows/release-notes.yml`

Chi tiết vận hành deploy: `backend/docs/DEPLOYMENT_RUNBOOK.md`

## 10. Lưu ý bảo mật và vận hành

- Không commit thông tin nhạy cảm vào file env.
- Không dùng secret mặc định ở staging/production.
- Khi thay đổi route map, backend image hoặc gateway config, cần rebuild + recreate để tránh runtime stale.
- Khi có sự cố bảo mật, theo checklist trong `backend/docs/SECURITY_RUNBOOK.md`.
