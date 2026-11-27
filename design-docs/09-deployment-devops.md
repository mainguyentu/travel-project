# 09 - Deployment & DevOps

## 1. Mục tiêu vận hành hiện tại

- Đóng gói backend, gateway, frontend và hạ tầng phụ trợ bằng Docker.
- Chạy local bằng `docker-compose.yml`; chạy staging/production bằng `docker-compose.deploy.yml`.
- Chuẩn hóa CI/CD với các workflow tách lớp: quality, build image, deploy, post-deploy SLO check.

## 2. Runtime topology đang áp dụng

### 2.1 Local compose

- `api-gateway` (Nginx)
- `backend` (FastAPI app phục vụ API)
- `frontend` (Laravel SSR)
- `worker` (Kafka consumer cập nhật analytics/read model)
- `postgres`
- `redis`
- `kafka`
- `elasticsearch`

### 2.2 Deploy compose (staging/production)

- `api-gateway`
- `backend`
- `worker`
- `postgres`
- `redis`
- `kafka`
- `elasticsearch`

Ghi chú: không còn tách runtime `frontend-public`/`frontend-admin`; frontend hiện là một ứng dụng Laravel với route group theo role.

## 3. Môi trường

- `local`: dùng để phát triển và kiểm thử tích hợp nhanh.
- `staging`: môi trường pre-prod cho UAT và verify pipeline.
- `production`: có manual approval + deploy gate rõ ràng.

## 4. CI/CD đã triển khai

### 4.1 Quality gate

Workflow: `.github/workflows/repo-quality.yml`

- Backend tests + coverage gate (`pytest --cov-fail-under=70`).
- Frontend build + feature tests (PHPUnit + coverage artifact).
- Security scan:
	- `pip-audit` (Python deps)
	- `composer audit` (PHP deps)
	- `npm audit` (Node deps)
	- `trivy` scan backend image (HIGH/CRITICAL)

### 4.2 Build & publish image

Workflow: `.github/workflows/release-build.yml`

- Trigger sau khi `Repo Quality` thành công (hoặc manual dispatch).
- Build/push image lên GHCR:
	- `ghcr.io/<repo>/backend:<tag>`
	- `ghcr.io/<repo>/api-gateway:<tag>`

### 4.3 Deploy staging

Workflow: `.github/workflows/deploy-staging.yml`

- Trigger sau `Release Build` thành công (main).
- SSH vào host staging, pull image, `docker compose -f docker-compose.deploy.yml up -d`.
- Chạy reusable workflow `post-deploy-slo-check` sau deploy.

### 4.4 Deploy production

Workflow: `.github/workflows/deploy-production.yml`

- Có commit message gate (`[deploy]`) cho auto flow.
- Có manual confirmation phrase (`DEPLOY_PRODUCTION`) cho manual flow.
- Có bước manual approval trước deploy thực tế.
- Hỗ trợ rollback theo tag (`rollback_to_tag`).
- Chạy `post-deploy-slo-check` sau deploy.

### 4.5 SLO verification sau deploy

Workflow: `.github/workflows/post-deploy-slo-check.yml`

- Kiểm tra endpoint:
	- `/health`
	- `/api/v1/destinations?page=1&limit=5`
	- `/api/v1/analytics/summary`
- Gate theo ngưỡng latency cấu hình theo môi trường.

## 5. Config & secrets

- Config tách theo biến môi trường (`.env` local, secrets runtime cho CI/CD).
- Không commit credentials/secrets vào repo.
- Secrets deploy bắt buộc cho SSH/GHCR/Base URL nằm trong GitHub Secrets.

## 6. Backup & recovery (baseline hiện tại)

- PostgreSQL: yêu cầu backup định kỳ và kiểm thử restore theo runbook hạ tầng.
- Elasticsearch/Kafka: giữ baseline snapshot/config backup cho môi trường production.
- Production workflow đã có cơ chế rollback theo image tag.

## 7. Runbook liên quan

- `backend/docs/DEPLOYMENT_RUNBOOK.md`
- `backend/docs/SECURITY_RUNBOOK.md`
- `backend/docs/WORKER_RUNBOOK.md`
- `backend/docs/OBSERVABILITY_BASELINE.md`

## 8. Connection Pooling Baseline

Mục này chuẩn hóa yêu cầu pooling đã chốt trong understanding-lock.

### 8.1 Gateway pooling (Nginx)

- Bật keepalive cho upstream backend.
- Dùng HTTP/1.1 upstream để tái sử dụng kết nối.
- Theo dõi số lượng upstream connection đang mở và tỉ lệ reset connection.

### 8.2 Backend DB pooling (PostgreSQL)

- Cấu hình qua biến môi trường:
	- `DB_POOL_SIZE`
	- `DB_MAX_OVERFLOW`
	- `DB_POOL_TIMEOUT`
	- `DB_POOL_RECYCLE`
- Bật health check kết nối (`pool_pre_ping`).
- Alert khi có timeout chờ connection hoặc pool exhausted.

### 8.3 Backend Redis pooling

- Dùng connection pool tại Redis client.
- Cấu hình giới hạn connection theo môi trường (local/staging/prod).
- Alert khi timeout Redis hoặc connection bị từ chối tăng bất thường.

### 8.4 Frontend outbound HTTP pooling

- Ưu tiên reuse connection trong HTTP client tới API Gateway.
- Giới hạn request burst theo trang/chức năng để tránh spike không cần thiết.

### 8.5 Checklist xác nhận trước release

- Quality workflow pass.
- Build image và push registry thành công.
- Deploy staging thành công + SLO check pass.
- Production deploy có approval hợp lệ và có rollback plan theo tag.
