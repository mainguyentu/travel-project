# U4 + U5 — Resolution record (owner decisions 2026-11-27)

## U4 — Quality gates: owners, blocking vs advisory (XSTD-002)

Owner mặc định mọi gate: **project owner** (cho đến khi chỉ định người khác).

| Gate (workflow `repo-quality.yml`) | Loại | Ngưỡng pass |
|---|---|---|
| Backend `pytest` (job `backend`) | **blocking** | toàn bộ tests pass sau migrate + seed |
| Frontend `phpunit` (job `frontend`) | **blocking** | toàn bộ tests pass |
| `docker compose config` (job `compose-static`) | **blocking** | parse hợp lệ, exit 0 |
| `pip-audit` (step trong job `backend`) | **advisory** | `|| true` — không chặn merge; lên **blocking** khi hết CVE HIGH chưa fix |

- Trivy / image scan: chưa có workflow — giữ **advisory**, thêm vào backlog khi bật.
- Branch protection: yêu cầu bật thủ công trên GitHub (bắt buộc pass `repo-quality`)
  — việc của owner, ghi backlog Pha D-1, không thuộc code change lần này.

## U5 — Contract change: approval + compatibility window (XSTD-001-R007)

- Mọi thay đổi `documents/contracts/BE-API-*` / `FE-*` do **project owner duyệt**.
- Compatibility window: hỗ trợ **1 minor** (N và N-1); breaking change chỉ ở
  **major** kèm migration notes trong contract doc.
- Baseline hiện tại: BE `1.2.0`, FE `1.1.0` (từ `1.0.0-MVP` / `1.1.0`).
