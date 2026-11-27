# Design Docs Index

Bộ `design-docs` là nguồn thiết kế và implementation planning của Travel Project. Thư mục này dùng để:

- Chốt requirement và phạm vi.
- Đồng bộ architecture/API/database/workflow trước khi code.
- Theo dõi gap giữa thiết kế và implementation qua task board.

Cập nhật: 2026-04-24

## 1. Cách đọc để nhoát nhanh dự án

Lượt đọc khuyến nghị:

1. `00-understanding-lock.md`
2. `01-system-architecture.md`
3. `02-api-design.md`
4. `03-database-design.md`
5. `04-workflows.md`
6. `08-auth-security.md`
7. `09-deployment-devops.md`
8. `10-testing-quality.md`
9. `GAP_TASK_BOARD.md`

## 2. Mục lục bộ tài liệu

Khối requirement và architecture:

1. `00-understanding-lock.md` - Nguồn yêu cầu đã khóa.
2. `01-system-architecture.md` - Kiến trúc tổng thể và boundaries.
3. `02-api-design.md` - API contract và error model.
4. `03-database-design.md` - Schema/index/migration strategy.
5. `04-workflows.md` - Workflow nghiệp vụ và workflow hệ thống.

Khối frontend và UX:

6. `05-ux-ui-guidelines.md` - Quy tắc UX/UI.
7. `06-frontend-interface-design.md` - Thiết kế giao diện frontend.
8. `07-frontend-routes.md` - Route map frontend.

Khối security/devops/quality:

9. `08-auth-security.md` - Auth và security controls.
10. `09-deployment-devops.md` - Compose, CI/CD, vận hành.
11. `10-testing-quality.md` - Test strategy và quality gates.
12. `11-coding-conventions.md` - Quy ước coding.
13. `12-api-docs-gateway.md` - Mô hình docs portal tại gateway.

Khối mở rộng/chuyên đề:

14. `13-destination-image-cloudinary-plan.md` - Kế hoạch migrate image.
15. `14-activity-recommendation-design.md` - Thiết kế recommendation.
16. `activice_plan.md` - Tài liệu planning bổ sung.
17. `activity-recommendation-implementation-plan.md` - Kế hoạch thực thi recommendation.

Tracking:

18. `GAP_TASK_BOARD.md` - Bảng theo dõi gap và backlog.

## 3. Quy tắc cập nhật design-docs

- Mọi thay đổi contract API phải cập nhật `02-api-design.md` và đối chiếu với `backend/docs/API_REFERENCE.md`.
- Mọi thay đổi schema phải cập nhật `03-database-design.md` và migration liên quan.
- Mọi thay đổi route/frontend flow phải cập nhật `06-frontend-interface-design.md` và `07-frontend-routes.md`.
- Mọi thay đổi release/process phải cập nhật `09-deployment-devops.md` và `GAP_TASK_BOARD.md`.

## 4. Đối chiếu với tài liệu implementation

- Tổng quan project: `../README.md`
- Backend implementation docs: `../backend/docs/README.md`
- Backend API reference: `../backend/docs/API_REFERENCE.md`
- Backend architecture runbook: `../backend/docs/ARCHITECTURE.md`
- Frontend implementation docs: `../frontend/README.md`

## 5. Trạng thái tài liệu hiện tại

- Bộ tài liệu có đầy đủ các khối requirement, architecture, implementation plan.
- Đã bổ sung tài liệu thiết kế cho destination image và activity recommendation.
- Cần duy trì cập nhật định kỳ theo sprint để tránh drift giữa thiết kế và codebase.
