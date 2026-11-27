# Báo cáo Pha C — Hardening + Observability

Ngày: 2026-11-27 | Ngưỡng owner chốt giữ: **IP 120/phút, user 60/phút** | Trạng thái: **HOÀN THÀNH**

## 1. Việc đã làm

Backend (`backend/`):
- `core/rate_limit.py` (mới): sliding-window in-memory — IP 120/phút
  (check trước auth), user-key 60/phút (check sau auth, khi có `current_user`).
  Vượt → `429 {code:RATE_LIMITED, meta:{retry_after}}` + header `Retry-After`.
  Miễn `/health`, `/api/v1/health`. `reset_buckets()` cho test.
- `app_factory.py`: + middleware rate-limit; + security headers mọi response
  (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: same-origin`, giữ `X-Request-Id`).
- `routers/observability.py` (mới, mount ngoài `/api/v1` qua `no_prefix`):
  `GET /metrics` (Prometheus text: uptime + 2 ngưỡng limit),
  `GET /ready` (`{ready, checks:{postgres, redis, elasticsearch}}`).
- `services/admin.py`: index đồng bộ ES khi create/update/bulk
  (`_index_sync` + `remove_destination` khi delete) — test tạo xong search thấy ngay.
- `routers/admin.py`: audit đầy đủ mọi action —
  `user_status|user_role`, category create/update/delete,
  destination create/update/delete (+ `bulk_create` đã có Pha A).
- `tests/test_phase_c.py` (mới, 5 tests): rate-limit 429 shape, headers,
  metrics/ready, audit ghi sau action.

Gateway/infra:
- `nginx.conf`: `limit_req_zone 120r/m + burst 20` cho `/api/v1/`;
  giữ security headers; proxy `/metrics`, `/ready` về backend.
- `documents/RUNBOOK.md` (mới): check nhanh, ngưỡng limit, bảng sự cố,
  backup/restore tối thiểu, deploy/rollback.

## 2. Verification

| Check | Kết quả |
|---|---|
| Backend pytest (container) | **22 passed** (17 + 5 Pha C) |
| Frontend phpunit | **12 passed, 39 assertions** |
| Smoke P3 qua gateway | **5/5** |
| `/metrics`, `/ready` qua gateway | text Prometheus + `{ready:true, checks all ok}` |
| 429 shape | `RATE_LIMITED + retry_after + Retry-After` (unit) |

## 3. Gaps / quyết định còn mở

- Rate-limit in-memory (mất khi restart, single-replica) — scale-out cần
  Redis-backed counter (ghi trong runbook).
- ES single-node không TLS/auth nội bộ (chấp nhận cho dev compose).
- `/ready` trả 200 kèm `ready:false` khi pg/redis lỗi (chưa 503 — để Pha D SLO quyết).
- U1..U7 trong `STANDARDS-PROFILE.md` vẫn mở.

## 4. Tiếp theo

**Pha D — Pipeline CI/CD + Docs/Board**: lint/test/build/push images,
deploy staging/production, SLO post-deploy, release notes; đồng bộ
`GAP_TASK_BOARD.md` theo codebase mới; điền `figma-guidelines` nếu cần;
G3 release decision mới.
