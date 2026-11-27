# 12. API Docs Gateway

## Mục tiêu

Thiết kế một gateway tài liệu tập trung cho toàn bộ Swagger/OpenAPI của hệ thống Travel Project, để một URL duy nhất có thể:

- Liệt kê tất cả API service.
- Mở nhanh Swagger UI hoặc Redoc cho từng service.
- Cung cấp OpenAPI JSON chuẩn cho tooling, QA, và AI agents.
- Không làm xung đột với frontend Laravel đang chiếm route `/` qua gateway hiện tại.

## Bối cảnh hiện tại

Hệ thống đang chạy theo mô hình service-split:

- `auth-service`
- `destination-service`
- `interaction-service`
- `admin-service`
- `analytics-service`

Gateway hiện tại là Nginx reverse proxy. Nó chỉ route request API theo prefix, còn các route non-API đi về frontend.

Điểm quan trọng:

- Swagger mặc định của FastAPI nằm ở `/docs`.
- OpenAPI JSON mặc định nằm ở `/openapi.json`.
- Qua gateway hiện tại, các đường dẫn này không nên dùng trực tiếp ở root vì sẽ đụng frontend route và không nhất quán với route map service-split.

## Khuyến nghị kiến trúc

### Phương án được khuyến nghị

Dùng một docs portal đặt dưới gateway, ví dụ:

- `GET /api-docs` -> trang portal trung tâm
- `GET /api-docs/specs/auth.json` -> OpenAPI JSON của auth service
- `GET /api-docs/specs/destination.json` -> OpenAPI JSON của destination service
- `GET /api-docs/specs/interaction.json` -> OpenAPI JSON của interaction service
- `GET /api-docs/specs/admin.json` -> OpenAPI JSON của admin service
- `GET /api-docs/specs/analytics.json` -> OpenAPI JSON của analytics service

Portal này render:

- danh sách service;
- nút mở Swagger UI theo service;
- dropdown chọn spec;
- link copy nhanh cho QA/LLM tooling.

### Vì sao chọn cách này

- Không cần merge spec thành một file khổng lồ.
- Giữ ranh giới service rõ ràng.
- Dễ versioning từng service.
- Dễ gắn auth riêng cho từng docs nếu cần.
- Không phụ thuộc frontend Laravel.
- Phù hợp với Nginx gateway hiện có.

## Luồng truy cập

```text
User / QA / AI agent
    |
    v
GET /api-docs
    |
    v
Nginx gateway serves static docs portal
    |
    +--> GET /api-docs/specs/auth.json       -> auth-service /openapi.json
    +--> GET /api-docs/specs/destination.json -> destination-service /openapi.json
    +--> GET /api-docs/specs/interaction.json -> interaction-service /openapi.json
    +--> GET /api-docs/specs/admin.json       -> admin-service /openapi.json
    +--> GET /api-docs/specs/analytics.json   -> analytics-service /openapi.json
```

## Route map đề xuất

| Gateway path | Target | Mục đích |
|---|---|---|
| `/api-docs` | Static docs portal | Trang index trung tâm |
| `/api-docs/specs/auth.json` | `auth-service:8000/openapi.json` | Spec auth |
| `/api-docs/specs/destination.json` | `destination-service:8000/openapi.json` | Spec public + destination |
| `/api-docs/specs/interaction.json` | `interaction-service:8000/openapi.json` | Spec user interaction |
| `/api-docs/specs/admin.json` | `admin-service:8000/openapi.json` | Spec admin |
| `/api-docs/specs/analytics.json` | `analytics-service:8000/openapi.json` | Spec analytics |

## UI của docs portal

Portal chỉ cần là một static page, không cần backend riêng nếu nhu cầu hiện tại chỉ là browse docs.

Nội dung tối thiểu:

- Title: `Travel API Docs`
- Service cards với mô tả ngắn
- Nút `Open Swagger UI`
- Nút `Open OpenAPI JSON`
- Filter theo service/domain
- Hiển thị build/version nếu có metadata từ spec

Nếu muốn trải nghiệm tốt hơn, portal có thể embed Swagger UI và đổi spec động bằng query string, ví dụ:

- `/api-docs?service=auth`
- `/api-docs?service=admin`

## Chiến lược triển khai spec

### Cấp 1: Không chạm backend code

Gateway chỉ proxy các JSON spec hiện có từ từng service.

Ưu điểm:

- nhanh;
- ít rủi ro;
- không đụng code business.

### Cấp 2: Chuẩn hóa metadata docs

Mỗi service nên bổ sung:

- `title`
- `description`
- `version`
- `tags`
- server URLs phù hợp môi trường local/staging/prod

### Cấp 3: Tích hợp CI validation

Thêm kiểm tra:

- OpenAPI JSON hợp lệ;
- link docs không gãy;
- portal route tồn tại;
- không có spec nào bị lệch prefix.

## Security considerations

- Không expose docs nhạy cảm trên production nếu spec chứa route nội bộ hoặc schema chưa công khai.
- Có thể bảo vệ `/api-docs` bằng basic auth, VPN, hoặc allowlist IP ở staging/prod.
- Không nhúng secret, token, internal hostnames vào portal.
- Nếu service admin/analytics cần hạn chế, có thể tách quyền xem docs theo role.

## Gợi ý Nginx implementation

- Giữ route hiện tại cho API traffic.
- Thêm block riêng cho `/api-docs`.
- Dùng `proxy_pass` cho `/api-docs/specs/*.json` sang từng service.
- Serve static portal từ Nginx container hoặc một docs container nhỏ.

Quan trọng nhất:

- Không dùng `/docs` ở root gateway nếu frontend vẫn giữ catch-all `/`.
- Dùng một prefix riêng như `/api-docs` để tránh xung đột route.

## Rollout plan

1. Chốt URL chuẩn cho docs portal.
2. Tạo static portal.
3. Map từng spec JSON qua gateway.
4. Test trên local Docker Compose.
5. Cập nhật tài liệu onboarding và runbook.
6. Nếu cần, thêm bảo vệ auth cho docs trên môi trường non-local.

## Acceptance criteria

- Một URL duy nhất mở được portal docs.
- Mỗi service có link OpenAPI JSON riêng.
- Không ảnh hưởng route frontend Laravel.
- Không thay đổi logic nghiệp vụ backend.
- Docs vẫn hoạt động khi chạy full stack qua Docker Compose.
