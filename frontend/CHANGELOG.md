# Frontend Changelog

Lịch sử thay đổi cho phần frontend của dự án `travel-project`.

Ghi chú:

- Changelog này theo ngữ cảnh sản phẩm, không theo skeleton gốc của Laravel.
- Release notes tự động ở mức repository dùng workflow: `.github/workflows/release-notes.yml`.

## [Unreleased]

- Đồng bộ tài liệu frontend với runtime hiện tại (popup detail flow, auth/session flow, link docs hệ thống).
- Chuẩn hóa mô tả tích hợp với API Gateway (`http://localhost:8080`) và chạy local (`http://127.0.0.1:8000`).

## [2026-04-02]

- Thay thế toàn bộ changelog skeleton của Laravel bằng changelog theo sản phẩm thực tế.
- Liên kết rõ với release workflow tại repository root.

## [2026-04-01]

- Cập nhật README frontend với luồng public/user/admin theo codebase.
- Đồng bộ tài liệu liên quan backend (`API_REFERENCE`, `ARCHITECTURE`, `DEPLOYMENT_RUNBOOK`).

## [2026-03-31]

- Hoàn thiện nhóm test tính năng frontend (`PublicFlowTest`, `AuthFlowTest`, `AdminFlowTest`, `MiddlewareAccessTest`).
- Cố định baseline build/test trong quality pipeline.
