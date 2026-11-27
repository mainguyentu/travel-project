# 10 - Testing & Quality

## 1. Mục tiêu chất lượng hiện tại

- Đảm bảo tính đúng đắn nghiệp vụ core: auth, destinations, interaction, admin, analytics.
- Giữ quality gate ổn định trên CI trước khi build/deploy.
- Theo dõi SLO sau deploy qua workflow tự động.

## 2. Test pyramid

- Unit test (service/business logic)
- Integration test (API + DB + cache)
- E2E/smoke test (luồng chính user + admin + analytics)

## 3. Test scope theo module

### 3.1 Auth
- Backend: register/login/refresh/logout flow qua API.
- Frontend: login/register/logout flow và session state.
- Middleware access theo role user/admin.

### 3.2 Destination
- API list + filter + pagination.
- Detail endpoint và dữ liệu trả về.
- Frontend destinations index với query param mapping đúng sang API.

### 3.3 Interaction
- Favorite idempotent.
- Rating upsert theo 1 user/1 destination.
- Event-driven update read model (analytics counters).

### 3.4 Admin
- API CRUD category/destination/user status.
- Frontend admin dashboard/users/categories/destinations/stats rendering.

### 3.5 Analytics & worker

- Worker handler cập nhật metrics từ event (`favorite.created`, `rating.upserted`, `destination.viewed`).
- Analytics summary/top endpoints trả dữ liệu hợp lệ.

## 4. Non-functional tests

- Rate limit behavior test đã có trong backend suite.
- Smoke E2E qua API Gateway để verify luồng end-to-end với hạ tầng compose.
- Post-deploy SLO check (latency threshold) ở staging/production.

## 5. Test suites đang có trong repo

### 5.1 Backend

- `backend/tests/test_health.py`
- `backend/tests/test_api.py`
- `backend/tests/test_rate_limit_search_perf.py`
- `backend/tests/test_analytics_worker.py`
- `backend/tests/test_smoke_e2e.py`

### 5.2 Frontend

- `frontend/tests/Feature/PublicFlowTest.php`
- `frontend/tests/Feature/AuthFlowTest.php`
- `frontend/tests/Feature/AdminFlowTest.php`
- `frontend/tests/Feature/MiddlewareAccessTest.php`

## 6. Quality gates trong CI

- Backend tests pass với coverage gate (`--cov-fail-under=70`).
- Frontend build + feature tests pass.
- Dependency scan pass (pip/composer/npm) và image scan trivy chạy đầy đủ.
- Artifact coverage và security reports được upload sau mỗi run.

Workflow tham chiếu: `.github/workflows/repo-quality.yml`.

## 7. Acceptance checklist (theo trạng thái hiện tại)

- [x] Guest xem/lọc list + xem detail hoạt động ổn định
- [x] User login + favorite + rating hoạt động đúng
- [x] Admin CRUD cơ bản user/category/destination đã có test flow
- [x] Dashboard top favorites/ratings/views có test rendering và API source
- [x] SLO check sau deploy đã có gate tự động (`post-deploy-slo-check`)

## 8. Gap còn mở

- Chưa có load/soak test chuyên biệt ở mức throughput cao (ngoài smoke + perf baseline).
- Chưa có threshold coverage tổng hợp đa dịch vụ thành một quality gate duy nhất.
- Cần bổ sung regression suite cho các incident đã đóng (nếu có) theo runbook QA.
