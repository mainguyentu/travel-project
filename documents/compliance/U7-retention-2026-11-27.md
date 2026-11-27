# U7 — Evidence retention / audit cadence (owner decision 2026-11-27)

## Quyết định

- Giữ báo cáo compliance + artifact CI (release-build logs): **12 tháng**.
- Audit lại khi: đổi boundary/stack, đổi exposure (HTTP→HTTPS public), hoặc
  **6 tháng/lần** — lấy gần nhất làm hạn.
- `audit_logs` DB (admin actions): giữ theo U6 retention (7 bản backup ≈ 7 ngày
  khôi phục được; log gốc trong DB giữ đến khi DB prune thủ công — backlog: job prune).
- Nơi lưu: `documents/compliance/` trong repo (versioned cùng code).

## Lịch audit tiếp theo

- Hạn audit định kỳ đầu tiên: **2026-05-27** (6 tháng sau 2026-11-27) hoặc sớm hơn
  khi gỡ G3 HOLD / public thật.
