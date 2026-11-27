# 08 - Auth & Security

## 1. Authentication model

- Cơ chế chính: JWT (access + refresh token)
- OAuth2: lớp tích hợp mở rộng cho social login hoặc identity provider bên ngoài.

## 2. Token strategy

- Access token TTL ngắn (ví dụ: 15-60 phút).
- Refresh token TTL dài hơn (ví dụ: 7-30 ngày).
- Có revoke token tại logout hoặc khi user bị khóa.

## 3. Password policy

- Hash bằng bcrypt.
- Không lưu plaintext password.
- Áp rule độ mạnh tối thiểu.

## 4. Authorization

- Role-based access control:
  - `user`
  - `admin`
- Route admin kiểm tra role bắt buộc.

## 5. Security controls theo NFR

- HTTPS everywhere.
- Chống SQL injection: ORM + parameterized query.
- Chống XSS: escape output ở template, sanitize input comment nếu cần render HTML.
- Chống CSRF cho form web session flow.
- Rate limiting tại gateway (IP + user).

## 6. API hardening

- Validate input bằng schema (Pydantic).
- Giới hạn kích thước payload.
- Không trả stack trace nội bộ ra client.
- Dùng request id để trace.

## 7. Audit & logging

- Log auth event: login success/fail, refresh, revoke.
- Log admin action: CRUD destination/category/user updates.
- Mask dữ liệu nhạy cảm trong log.

## 8. Security checklist trước release

- [ ] TLS config chuẩn production
- [ ] Secret management qua env/secret store
- [ ] JWT secret rotation plan
- [ ] Rate limit đã bật cho endpoint auth
- [ ] CORS chỉ cho phép origin hợp lệ
- [ ] Kiểm tra dependency vulnerabilities
