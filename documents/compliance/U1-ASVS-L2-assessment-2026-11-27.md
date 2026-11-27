# U1 — ASVS L2 Assessment (owner chốt L2, 2026-11-27)

Phạm vi: backend FastAPI monolith + frontend Laravel Blade + gateway nginx (dev compose).
Phương pháp: review code + config (không pentest ngoài).

## Kết quả theo nhóm ASVS 4.0 L2

| Nhóm | Hiện trạng | Kết luận |
|---|---|---|
| 2.1 Password security | Register `min_length=6` (BE + FE) — yếu so với L2 | **Finding F1 → đã fix: nâng lên 8** (`backend/app/schemas/auth.py`, `frontend/.../AuthController.php`) |
| 2.1 Credential recovery | Chưa có quên/reset password | **Gap G1** — ngoài MVP, ghi backlog (không chặn G3 hold vì tính năng bỏ ngõ) |
| 2.2 Authenticator lifecycle | bcrypt hash, login generic error, locked user 403, refresh rotate + revoke, logout revoke | **Pass** |
| 2.3 Authenticator recovery | Không có self-service recovery | **Gap G1** (như trên) |
| 3.1 Session binding | JWT access 30' + refresh 14d, type check, iss check; FE session file + HttpOnly + SameSite lax | **Pass** (lưu ý: `SESSION_SECURE_COOKIE` chưa set — **Finding F2**: bật `secure=true` khi chạy HTTPS production, dev HTTP giữ nguyên) |
| 3.2 Session termination | Logout revoke refresh; refresh reuse → 401 | **Pass** |
| 4.1 Access control | `require_admin` router guard + `get_current_user` check active; internal key header | **Pass** |
| 5.1 Input validation | Pydantic Field min/max/pattern mọi schema; validation error shape không lộ input/ctx | **Pass** |
| 7.1 Log + 7.2 Rate limit | Audit logs admin action; rate-limit 2 lớp IP 120/user 60 + 429 shape + Retry-After | **Pass** |
| 8.3 Sensitive data | `password_hash` Text, không log password; JWT_SECRET default dev trong compose | **Finding F3**: production MUST set `JWT_SECRET` + `INTERNAL_API_KEY` mạnh qua env (compose đã `${VAR:-default}` — đúng pattern, chỉ cần checklist deploy) |
| 9.1 TLS | Dev HTTP (hợp lệ); chưa có TLS termination | **Gap G2**: production cần TLS ở gateway/LB + `SESSION_SECURE_COOKIE=true` |
| 14.4 HTTP headers | Backend + nginx đều set nosniff/DENY/same-origin; `server_tokens off`; `client_max_body_size 1m` | **Pass** |

## Fix đã áp dụng (lần này)

- F1: password register `min_length` 6 → **8** (BE schema + FE validate).
- F2/F3/G2: không đổi code — ghi vào checklist deploy trong RUNBOOK (bước U6).

## Còn lại (không chặn code, thuộc deploy/backlog)

- G1: quên/reset password (tính năng bỏ ngõ theo owner).
- G2: TLS production + secure cookie (checklist deploy).
