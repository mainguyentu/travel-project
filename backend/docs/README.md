# Backend Docs Index

Tài liệu backend được chia theo 3 nhóm: technical reference, runbook vận hành, và deployment/security.

Cập nhật: 2026-04-24

## 1. Technical reference

- `API_REFERENCE.md`
  - Danh sách endpoint, request/response, feature flags và payload mẫu.
- `ARCHITECTURE.md`
  - Kiến trúc runtime, route map gateway, data flow, event flow.
- `INSIGHT_PROCESSING.md`
  - Quy trình khởi tạo/cập nhật insight, confidence blending, status model.

## 2. Operational runbooks

- `WORKER_RUNBOOK.md`
  - Vận hành worker, retry, DLQ, replay quy mô nhỏ đến lớn.
- `OBSERVABILITY_BASELINE.md`
  - Baseline SLO và guardrails cần theo dõi.

## 3. Security and deployment

- `SECURITY_RUNBOOK.md`
  - Secret rotation, incident checklist, audit log truy vết.
- `DEPLOYMENT_RUNBOOK.md`
  - CI/CD staging/production, rollback, post-deploy SLO checks.

## 4. Dùng tài liệu nào trong tình huống nào

- Cần tìm endpoint và payload: mở `API_REFERENCE.md`.
- Cần tra route map và service ownership: mở `ARCHITECTURE.md`.
- Cần debug chất lượng insight destination: mở `INSIGHT_PROCESSING.md`.
- Worker lỗi, DLQ tăng nhanh: mở `WORKER_RUNBOOK.md`.
- Chuẩn bị release/deploy: mở `DEPLOYMENT_RUNBOOK.md`.
- Incident bảo mật hoặc rotate secret: mở `SECURITY_RUNBOOK.md`.

## 5. Quy tắc cập nhật

- Thay đổi contract API: cập nhật `API_REFERENCE.md` và test liên quan.
- Thay đổi route map/service split: cập nhật `ARCHITECTURE.md`.
- Thay đổi insight algorithm: cập nhật `INSIGHT_PROCESSING.md`.
- Thay đổi deploy pipeline: cập nhật `DEPLOYMENT_RUNBOOK.md`.
- Mỗi cập nhật docs nên ghi ngày cập nhật ở đầu file.
