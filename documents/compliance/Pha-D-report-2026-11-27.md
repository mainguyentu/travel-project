# Báo cáo Pha D — Pipeline CI/CD + Docs/Board

Ngày: 2026-11-27 | Trạng thái: **HOÀN THÀNH**

## 1. Việc đã làm

CI/CD (`.github/workflows/`, 6 files):
- `repo-quality.yml` (viết lại cho monolith mới): backend job
  (postgres:16 + redis:7 services, `alembic upgrade` + seed + `pytest`,
  ES/EVENTS tắt, pip-audit advisory) + frontend job (PHP 8.4, composer,
  key:generate, phpunit) + compose static validate.
- `release-build.yml` (viết lại): build/push 3 images
  (`travel-backend/frontend/gateway:tag`) lên GHCR khi push tag `v*`
  + Trivy scan backend image (HIGH/CRITICAL).
- `deploy-staging.yml` / `deploy-production.yml` (viết lại dạng template):
  `workflow_dispatch` theo tag, production dùng `environment: production`
  (approval qua GitHub reviewers), job `slo` gọi reusable
  `post-deploy-slo-check.yml` với secrets `STAGING/PROD_BASE_URL`.
- Giữ nguyên 2 workflows cũ còn dùng được: `post-deploy-slo-check.yml`
  (latency thresholds + artifact `slo-report-*`), `release-notes.yml`
  (release-drafter).
- Local: `scripts/slo_check.py` (mới, 5 checks production-safe,
  read-only trừ admin login) + `scripts/ci.ps1` += bước SLO local.

Docs/Board:
- `design-docs/GAP_TASK_BOARD.md` viết lại theo codebase mới
  (thay snapshot 2026-04-24 DONE-giả): MVP+Pha A/B/C/D DONE kèm evidence,
  G3 OPEN, 8 backlog OPEN, DoD mới.
- `figma-design/guidelines/Guidelines.md` (viết lại từ template trống):
  layouts, components, quy ước hiển thị, danh sách "không làm".
- `documents/RUNBOOK.md` (từ Pha C) + 4 báo cáo pha A–D trong
  `documents/compliance/`.

## 2. Verification

| Check | Kết quả |
|---|---|
| Workflows YAML parse | 6/6 ok |
| `scripts/slo_check.py` local qua gateway | **5/5** |
| Backend pytest (container) / frontend phpunit | 22 / 12 (không regression Pha D) |
| `docker compose config` | hợp lệ (lớp compose-static trong CI) |

## 3. Gaps / cần owner (không tự chốt)

1. Branch protection + GitHub Environments reviewers (backlog 1–2).
2. Secrets thật (`STAGING/PROD_BASE_URL`, deploy SSH) + runner/shop deploy thật
   (workflows deploy hiện là template).
3. `/ready` 503 khi degraded, rate-limit Redis-backed, ES TLS/auth (backlog 4–6).
4. U1..U7 trong `STANDARDS-PROFILE.md` vẫn mở.
5. **G3 release decision** (ship/hold) — thuộc về project owner.
