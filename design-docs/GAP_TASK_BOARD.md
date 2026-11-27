# Task Board — Codebase rewrite (Pha A–D), cập nhật 2026-11-27

> Thay thế snapshot cũ (2026-04-24, DONE theo codebase đã xóa).
> Legend: `DONE` = có code + test xanh trong repo hiện tại;
> `OPEN` = backlog chưa triển khai.

## Snapshot

| Pha | Trạng thái | Evidence |
|---|---|---|
| MVP rewrite (P0–P4 + G1/G2) | DONE | `documents/compliance/P4-gates-2026-11-27.md`; pytest 10, phpunit 11, smoke 5/5 |
| Pha A — Parity full-scope (BE 1.1.0/FE 1.1.0) | DONE | `documents/compliance/Pha-A-report-2026-11-27.md`; pytest 13, phpunit 12 |
| Pha B — Search + Async (BE 1.2.0) | DONE | `documents/compliance/Pha-B-report-2026-11-27.md`; pytest 17, ES `search_engine=elasticsearch` |
| Pha C — Hardening + Observability | DONE | `documents/compliance/Pha-C-report-2026-11-27.md`; pytest 22, `/metrics` + `/ready` |
| Pha D — Pipeline CI/CD + Docs/Board | DONE (bản này) | workflows + `slo_check.py` + board rewrite + guidelines |
| G3 release decision | OPEN (owner) | `documents/compliance/P4-gates-2026-11-27.md` §G3 |

## Backlog OPEN (sau Pha D)

1. Branch protection bắt buộc pass `repo-quality` trước merge `main`.
2. GitHub Environments (`staging`, `production`) + required reviewers (deploy-production dùng `environment: production` — cần cấu hình reviewers trên GitHub).
3. Secret scanning + policy gate cho PR.
4. `/ready` trả 503 khi `ready:false` (hiện 200 + flag — quyết SLO).
5. Rate-limit Redis-backed khi scale multi-replica (hiện in-memory).
6. ES TLS/auth nội bộ + retention/XTRIM policy cho Redis Streams.
7. Dashboard ingest artifact SLO theo thời gian.
8. Chuẩn hóa boundary docs B3..B10 theo monolith mới (hiện BOUNDARIES.md còn mô tả 5 services cũ).

## Definition of Done

- Tests liên quan pass (backend container + frontend local) + smoke/SLO qua gateway.
- Contract versioned (`BE-API-*.md`/`FE-*.md`) + báo cáo pha trong `documents/compliance/`.
- Không regression luồng auth/destinations/interaction/admin/analytics.
- U1..U7 giữ mở cho đến khi owner quyết (ghi trong `STANDARDS-PROFILE.md`).
