# Activity Recommendation Implementation Plan

## Goal
Triển khai tính năng Activity Recommendation pha 1 (MVP trên home) theo tài liệu thiết kế đã chốt, đảm bảo an toàn rollout và đủ kiểm thử trước khi bật production.

## Scope
- Bao gồm backend schema + seed + API + scoring + fallback + frontend home integration.
- Không bao gồm admin CRUD activity và không tách microservice ở pha 1.

## Tasks
- [ok] Tạo migration cho 4 bảng mới (`activities`, `destination_activities`, `activity_rules`, `destination_features`) và index cần thiết. → Verify: `alembic upgrade head` chạy thành công, DB có đủ bảng/index.
- [ok] Viết seed taxonomy activity + seed rules mặc định + seed mapping cơ bản (idempotent). → Verify: chạy seed 2 lần liên tiếp không tạo bản ghi trùng, số lượng dữ liệu ổn định.
- [ok] Tạo module repository cho activity catalog, mapping và rule lookup. → Verify: test repository trả đúng dữ liệu theo `activity_slug` và join đúng với destination insights.
- [ok] Cài Recommendation Engine (base_score, crowd_mode, final_score, threshold, ranking split). → Verify: unit test pass cho các case `prefer_low`, `prefer_high`, threshold và thứ tự sắp xếp.
- [ok] Expose endpoint `GET /api/v1/public/activities/{activity_slug}/recommendations` theo contract chuẩn. → Verify: trả đúng envelope `success/data/meta`, có `activity`, `highlight_destinations`, `recommended_destinations`, `trending`.
- [ok] Thêm cơ chế fallback lỗi nội bộ/timeout thành danh sách rỗng + `error_info` (mã lỗi nghiệp vụ). → Verify: test mô phỏng exception trả `success=true`, các list rỗng và có `endpoint_error_code`.
- [ok] Áp dụng rate limit theo IP cho endpoint recommendation public. → Verify: gửi burst request vượt ngưỡng nhận phản hồi bị giới hạn theo policy.
- [ok] Tích hợp frontend home section activity gọi endpoint mới và render 3 khối dữ liệu. → Verify: UI hiển thị đúng highlight/recommended/trending khi API OK.
- [ok] Hiển thị thông báo lỗi theo yêu cầu: “Lỗi API Endpoint + mã lỗi” khi có `error_info`. → Verify: mô phỏng fallback và xác nhận thông báo hiện đúng, layout không vỡ.
- [ok] Thiết lập feature flag rollout cho endpoint/integration và cấu hình theo 3 mốc rollout. → Verify: bật/tắt feature flag đổi đúng hành vi ở staging mà không cần sửa code.
- [ok] Bổ sung telemetry cơ bản (latency, fallback rate, empty-result rate) cho endpoint. → Verify: log/metric ghi nhận đủ nhãn `activity_slug` và xem được trên dashboard hiện có.
- [ok] Chạy bộ kiểm thử cuối cùng (backend unit+API, frontend integration, smoke) và cập nhật tài liệu API. → Verify: toàn bộ test liên quan pass, tài liệu cập nhật khớp hành vi thực tế.

## Critical Path
1. Migration + seed idempotent
2. Recommendation Engine + endpoint contract
3. Fallback + rate limit
4. Frontend home integration
5. Verification cuối và rollout staging

## Done When
- [ ] Endpoint recommendation chạy ổn định ở staging với P95 < 200ms trong tải baseline.
- [ ] Home hiển thị dữ liệu recommendation đúng và hiển thị lỗi đúng format khi fallback.
- [ ] Không có regression ở luồng public destinations hiện tại.
- [ ] Tài liệu thiết kế + API được cập nhật đầy đủ, sẵn sàng cho triển khai production.

## Notes
- Sau khi hoàn tất pha 1, chuẩn bị nhánh kiến trúc tách recommendation service bằng gateway upstream swap để không phá contract frontend.

## Progress Log
- 2026-04-23: Đã tạo migration `0006_activity_recommendation_core.py` (revision id: `0006_activity_reco_core`) cho Task 1 với 4 bảng mới và index theo thiết kế.
- 2026-04-23: Kiểm tra cú pháp file migration: không có lỗi.
- 2026-04-23: Verify runtime `alembic upgrade head` đang bị chặn do PostgreSQL local tại localhost:5432 chưa chạy (connection refused).
- 2026-04-23: Đã fix lỗi revision id quá dài gây lỗi cập nhật `alembic_version.version_num` và verify lại `alembic upgrade head` thành công đến revision `0006_activity_reco_core`.
- 2026-04-23: Đã thêm script `backend/scripts/seed_activity_recommendation.py` để seed taxonomy/rules/mapping/features theo hướng idempotent.
- 2026-04-23: Đã fix lỗi NOT NULL khi upsert `activities` (gán `name` trước khi `flush`).
- 2026-04-23: Verify idempotent chạy seed 2 lần liên tiếp, số lượng ổn định: `activities=5`, `activity_rules=5`, `destination_activities=0`, `destination_features=0` (DB hiện chưa có destination để map).
- 2026-04-23: Re-check DB thật: `destinations=503`.
- 2026-04-23: Seed lại trên dữ liệu thật thành công: `destination_activities=1430`, `destination_features=503`, chạy 2 lần liên tiếp counts ổn định.
- 2026-04-23: Đã thêm repository module [backend/app/repositories/activities.py](backend/app/repositories/activities.py) cho catalog/rules/mapping; expose tại [backend/app/repositories/__init__.py](backend/app/repositories/__init__.py).
- 2026-04-23: Đã thêm engine [backend/app/services/activity_recommendation.py](backend/app/services/activity_recommendation.py) với scoring, threshold, ranking split và trending độc lập.
- 2026-04-23: Verify pytest [backend/tests/test_activity_recommendation_engine.py](backend/tests/test_activity_recommendation_engine.py) pass: `2 passed`.
- 2026-04-23: Đã thêm endpoint public [backend/app/routers/activity_public.py](backend/app/routers/activity_public.py): `GET /api/v1/public/activities/{activity_slug}/recommendations`.
- 2026-04-23: Đã mount router vào [backend/app/main.py](backend/app/main.py) và [backend/app/apps/destination_service.py](backend/app/apps/destination_service.py).
- 2026-04-23: Verify contract endpoint qua pytest [backend/tests/test_api.py](backend/tests/test_api.py) với case `public_activity_recommendations_contract`: pass.
- 2026-04-23: Đã thêm fallback exception trong [backend/app/routers/activity_public.py](backend/app/routers/activity_public.py) trả `success=true` + list rỗng + `error_info`.
- 2026-04-23: Verify fallback qua pytest [backend/tests/test_api.py](backend/tests/test_api.py) với case `public_activity_recommendations_fallback_on_engine_error`: pass.
- 2026-04-23: Endpoint recommendation dùng middleware rate-limit IP/user hiện có tại [backend/app/app_factory.py](backend/app/app_factory.py).
- 2026-04-23: Verify rate limit cho endpoint recommendation qua pytest [backend/tests/test_api.py](backend/tests/test_api.py) với case `public_activity_recommendations_rate_limited_by_ip`: pass.
- 2026-04-23: Hoàn tất tích hợp frontend Home tại [frontend/app/Http/Controllers/HomeController.php](frontend/app/Http/Controllers/HomeController.php) và [frontend/resources/views/pages/public/home.blade.php](frontend/resources/views/pages/public/home.blade.php): gọi endpoint recommendation theo `activity_slug`, render 3 khối `highlight/recommended/trending`.
- 2026-04-23: Hoàn tất hiển thị lỗi fallback “Lỗi API Endpoint + mã lỗi” khi có `error_info` trên Home; cập nhật style hỗ trợ tại [frontend/resources/css/app.css](frontend/resources/css/app.css).
- 2026-04-23: Verify frontend integration qua `php artisan test tests/Feature/PublicFlowTest.php` pass `4 tests, 21 assertions`, gồm case render recommendation thành công và case banner lỗi fallback.
- 2026-04-23: Hoàn tất Task 10 feature flag rollout cho endpoint/integration: thêm cờ backend `ACTIVITY_RECOMMENDATION_ENDPOINT_ENABLED` trong [backend/app/core/config.py](backend/app/core/config.py), áp dụng gate include router tại [backend/app/main.py](backend/app/main.py) và [backend/app/apps/destination_service.py](backend/app/apps/destination_service.py).
- 2026-04-23: Thêm cờ frontend `FEATURE_ACTIVITY_RECOMMENDATION_ENDPOINT_ENABLED` và `FEATURE_ACTIVITY_RECOMMENDATION_HOME_ENABLED` tại [frontend/config/api.php](frontend/config/api.php), expose env trong [frontend/.env.example](frontend/.env.example), và gate integration trong [frontend/app/Http/Controllers/HomeController.php](frontend/app/Http/Controllers/HomeController.php) + [frontend/resources/views/pages/public/home.blade.php](frontend/resources/views/pages/public/home.blade.php).
- 2026-04-23: Verify rollout behavior qua test [frontend/tests/Feature/PublicFlowTest.php](frontend/tests/Feature/PublicFlowTest.php) pass `5 tests, 26 assertions`.
- 2026-04-23: Hoàn tất Task 11 telemetry cho endpoint recommendation tại [backend/app/routers/activity_public.py](backend/app/routers/activity_public.py): bổ sung structured telemetry log gồm `activity_slug`, `request_id`, `page`, `limit`, `budget_level`, `latency_ms`, `fallback_used`, `empty_result`, `endpoint_error_code`, và counts theo nhóm recommendation.
- 2026-04-23: Cập nhật baseline quan sát cho recommendation tại [backend/docs/OBSERVABILITY_BASELINE.md](backend/docs/OBSERVABILITY_BASELINE.md) với schema log event `activity_recommendation.telemetry` và hướng dẫn query latency/fallback/empty-result.
- 2026-04-23: Hoàn tất Task 12 verification: chạy `..\\.venv\\Scripts\\python.exe -m pytest tests/test_activity_recommendation_engine.py tests/test_api.py -q` pass `22 passed`; chạy `..\\.venv\\Scripts\\python.exe -m pytest tests/test_smoke_e2e.py -q` `1 skipped` (environment-dependent target); chạy `php artisan test tests/Feature/PublicFlowTest.php` pass `5 passed, 26 assertions`.
- 2026-04-23: Cập nhật tài liệu endpoint recommendation + rollout flags tại [backend/docs/API_REFERENCE.md](backend/docs/API_REFERENCE.md) để khớp hành vi thực tế.
