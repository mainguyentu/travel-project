# 14 - Thiết Kế Activity Recommendation (MVP Tích Hợp Home)

Cập nhật lần cuối: 2026-04-22.

## 1. Tóm Tắt Hiểu Bài

- Mở rộng hệ thống Travel để hỗ trợ gợi ý địa điểm theo Activity như khung trong activice_plan.md.
- Pha 1 là end-to-end MVP: backend recommendation + tích hợp vào home hiện tại.
- Không tạo trang activity riêng trong pha 1.
- Dữ liệu activity được quản lý bằng migration/seed thủ công, chưa có admin CRUD UI/API riêng.
- Scoring pha 1 là rule-based cố định theo activity, data-driven qua DB.
- Endpoint recommendation là public, áp dụng rate limit theo IP.
- Khi lỗi endpoint: trả danh sách rỗng và trả mã lỗi nghiệp vụ để frontend hiển thị thông báo Lỗi API Endpoint + mã lỗi.

## 2. Giả Định

- Insight dimensions được tái sử dụng từ hệ thống hiện có: scenery, accessibility, crowd, value.
- Frontend chỉ tích hợp trên home section activity.
- Contract response vẫn theo envelope API đang dùng toàn hệ thống.
- Team backend sở hữu logic recommendation pha 1, frontend consume API.

## 3. Nhật Ký Quyết Định

- D01: Chốt phạm vi pha 1 là end-to-end MVP.
- D02: Chỉ tích hợp trên home, không tạo route activity riêng.
- D03: Dữ liệu activity được nhập bằng migration/seed, chưa mở admin CRUD.
- D04: Rule-based scoring cố định theo activity (chưa personalization).
- D05: SLA endpoint recommendation: P95 < 200ms.
- D06: Scale theo baseline hiện tại: 1k MAU, 10k destinations, peak 20 req/s.
- D07: Security: public endpoint + rate limit theo IP.
- D08: Reliability: fallback trả rỗng + mã lỗi nghiệp vụ.
- D09: Ownership: backend team sở hữu toàn bộ logic recommendation pha 1.
- D10: Chọn phương án A: đặt engine trong backend hiện tại, chuẩn bị biên giới để tách service sau.
- D11: API contract ổn định ngay từ đầu để sau này chỉ đổi upstream routing tại gateway.
- D12: Rollout 3 mốc và feature flag để giảm rủi ro production.

## 4. Tóm Tắt Hướng Thiết Kế

Phương án được chọn: A.

- Đặt Activity Recommendation Engine trong backend hiện tại.
- Tách module rõ ràng theo domain bên trong service để tránh coupling với controller.
- Ưu tiên YAGNI cho pha 1, nhưng chuẩn bị sẵn cho pha tách microservice recommendation.

## 5. Kiến Trúc Và Ranh Giới Thành Phần

### 5.1 Ranh giới module

- Activity Catalog Module
  - Quản lý taxonomy activity.
  - Quản lý rule scoring theo activity.
- Destination-Activity Mapping Module
  - Quản lý quan hệ many-to-many destination và activity.
  - Lưu match weight theo destination-activity.
- Recommendation Engine
  - Tính điểm, xếp hạng, tách kết quả theo khối dữ liệu.
- Public Activity API
  - Expose endpoint cho home consume.
  - Xử lý validation input, rate limit, map response.

### 5.2 Tách lớp để tách service sau này

- Domain service theo hướng ports/adapters.
- API layer không chứa business logic scoring.
- Repository abstractions cho phép thay đổi storage path khi tách service.

## 6. Mô Hình Dữ Liệu Và Chiến Lược Migration

### 6.1 Bảng mới

1. activities
- id (PK)
- name
- slug (unique)
- description
- is_active
- created_at
- updated_at

2. destination_activities
- destination_id (FK -> destinations.id)
- activity_id (FK -> activities.id)
- weight (0..1, default 1.0)
- source (manual, seed)
- created_at
- updated_at
- PK composite: destination_id + activity_id

3. activity_rules
- activity_id (FK, unique)
- scenery_weight
- accessibility_weight
- crowd_weight
- value_weight
- crowd_mode (prefer_low hoặc prefer_high)
- min_match_threshold
- created_at
- updated_at

4. destination_features
- destination_id (PK/FK -> destinations.id)
- is_indoor
- is_outdoor
- suitable_time (day, night, both)
- budget_level
- duration_suggested_minutes
- created_at
- updated_at

### 6.2 Chỉ mục

- activities.slug unique index
- destination_activities(activity_id, destination_id)
- destination_activities(destination_id, activity_id)
- activity_rules(activity_id)

### 6.3 Kế hoạch rollout migration

- M1: Tạo bảng mới + index.
- M2: Seed activity taxonomy + seed rule mặc định.
- M3: Seed mapping destination-activity + destination_features cơ bản.
- M4: Backfill idempotent (upsert), cho phép chạy lại an toàn.

## 7. Hợp Đồng API

### 7.1 Endpoint

- GET /api/v1/public/activities/{activity_slug}/recommendations

### Query params

- page (default 1)
- limit (default 10)
- budget_level (optional)

### 7.2 Response envelope

- success
- data
  - activity
  - highlight_destinations
  - recommended_destinations
  - trending
  - error_info (nullable)
- meta

### error_info khi fallback

- endpoint_error_code
- endpoint_error_message

### 7.3 Hợp đồng fallback

Khi lỗi nội bộ/timeout:
- success vẫn true
- highlight_destinations = []
- recommended_destinations = []
- trending = []
- error_info có mã lỗi nghiệp vụ

## 8. Luồng Scoring Và Ranking

- Bước 1: Load activity theo slug.
- Bước 2: Load activity rule.
- Bước 3: Load candidate destinations qua destination_activities.
- Bước 4: Join destination_insights để lấy dimensions scoring.
- Bước 5: Tính base_score:
  - base_score = w1*scenery + w2*accessibility + w3*crowd_factor + w4*value
  - crowd_factor phụ thuộc crowd_mode.
- Bước 6: Tính final_score:
  - final_score = base_score * activity_match_weight
- Bước 7: Lọc theo min_match_threshold.
- Bước 8: Sort giảm dần theo final_score.
- Bước 9: Tách kết quả
  - highlight_destinations: top 1
  - recommended_destinations: danh sách phân trang
  - trending: top theo metric độc lập với final_score

## 9. Tích Hợp Frontend Trên Home

- Home section activity gọi endpoint theo activity slug.
- Render 3 khối dữ liệu: highlight, recommended, trending.
- Nếu có error_info thì hiện thông báo:
  - Lỗi API Endpoint + mã lỗi
- Layout không vỡ, danh sách giữ rỗng nếu fallback.

## 10. Yêu Cầu Phi Chức Năng

- Performance: P95 < 200ms.
- Scale: 1k MAU, 10k destinations, peak 20 req/s.
- Security: public endpoint + rate limit theo IP.
- Reliability: fallback trả rỗng + mã lỗi.
- Ownership: backend team.

## 11. Chiến Lược Kiểm Thử

### 11.1 Unit tests

- Score calculation theo từng activity rule.
- Crowd mode prefer_low / prefer_high.
- Threshold filter.
- Ranking ordering.

### 11.2 Repository tests

- Join đúng giữa activities, destination_activities, destination_insights, destination_features.

### 11.3 API contract tests

- Response shape đúng envelope.
- Paging recommended chính xác.
- Fallback response có error_info khi có lỗi.

### 11.4 Frontend integration tests

- Home render thành công với dữ liệu recommendation.
- Home render đúng thông báo Lỗi API Endpoint + mã lỗi khi fallback.

## 12. Kế Hoạch Triển Khai

- Rollout 1
  - Apply migration + indexes + seed taxonomy/rules/mapping.
- Rollout 2
  - Bật endpoint recommendation sau feature flag.
- Rollout 3
  - Bật home integration và monitor latency + error rate.

## 13. Đề Xuất Mở Rộng Cho Các Pha Sau

### 13.1 Product và data

- Bổ sung user preference profile để phục vụ personalization (nature affinity, food affinity, budget behavior).
- Bổ sung event tracking chi tiết cho activity click, recommendation click-through, conversion sang favorite/rating.
- Thiết kế quality score cho mapping destination-activity để đo độ tin cậy dữ liệu.

### 13.2 Tiến hóa kiến trúc

- Tách Recommendation Engine thành microservice riêng sau khi ổn định contract.
- Dùng gateway upstream swap để giữ nguyên API cho frontend.
- Cơ chế cache chia tầng (edge cache + app cache) để giảm p95 khi scale tăng.

### 13.3 Cải tiến ranking

- Rule-based + contextual boosts (day/night, indoor/outdoor, weather).
- Multi-objective ranking (chất lượng, độ mới, đa dạng kết quả).
- A/B testing cho weighting profile theo activity.

### 13.4 Vận hành

- Dashboard observability riêng cho activity endpoint (p95, timeout rate, fallback rate, empty-result rate).
- Alert theo ngưỡng fallback rate và p95 regression.
- Job re-balance rule weights theo lịch vận hành.

### 13.5 Governance và quality

- Quy trình review dữ liệu mapping activity định kỳ hàng tháng.
- Checklist release cho contract compatibility trước khi tách service.
- Data contract versioning cho response recommendation.

## 14. Rủi Ro Và Biện Pháp Giảm Thiểu

- Rủi ro mapping activity ban đầu chất lượng thấp.
  - Giảm thiểu: seed checklist + review mẫu + backfill iteration.
- Rủi ro score thiên lệch do weighting chưa tốt.
  - Giảm thiểu: telemetry theo activity_slug + tuning cycle.
- Rủi ro stale cache.
  - Giảm thiểu: TTL ngắn + invalidation theo update mapping/rule.

## 15. Tiêu Chí Kết Thúc Brainstorming

Hoàn tất brainstorming mode khi:
- Understanding lock được xác nhận.
- Design approach được chọn rõ ràng.
- Major assumptions, risks, decision log đã được ghi lại.
- Tài liệu đã được persist vào design-docs.
