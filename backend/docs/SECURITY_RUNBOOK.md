# SECURITY_RUNBOOK

Tài liệu vận hành bảo mật cho môi trường staging/production.

## 1) Secret Management

Áp dụng cho các biến: `JWT_SECRET`, `DATABASE_URL`, `REDIS_URL`, `KAFKA_BOOTSTRAP_SERVERS` và credential liên quan.

Nguyên tắc:

- Không commit secret vào repository.
- Luôn lưu secret ở secret manager của môi trường deploy.
- Mỗi secret cần owner và lịch rotation.
- Mọi thay đổi secret phải có ticket và log thay đổi.

## 2) Lịch Rotation tối thiểu

- `JWT_SECRET`: 90 ngày/lần hoặc ngay khi nghi ngờ lộ lọt.
- DB password: 90 ngày/lần.
- Redis password (nếu bật auth): 90 ngày/lần.
- Credential CI/CD deploy: 60 ngày/lần.

## 3) Quy trình Rotation JWT Secret

1. Tạo secret mới trong secret manager.
2. Cập nhật biến môi trường `JWT_SECRET` cho các service backend.
3. Rollout theo thứ tự: `auth-service` -> service còn lại -> `worker-service`.
4. Xác nhận endpoint `/health` và login/refresh hoạt động bình thường.
5. Theo dõi tỷ lệ lỗi `401`/`403` trong 15-30 phút.

Lưu ý:

- Sau rotation JWT, access/refresh token cũ sẽ không dùng được. Cần truyền thông trước cho team vận hành.

## 4) Incident Checklist (Security)

Khi phát hiện dấu hiệu xâm nhập hoặc rò rỉ secret:

1. Khoanh vùng phạm vi ảnh hưởng (service, credential, thời gian).
2. Tạm thời khóa đường truy cập bị nghi vấn (gateway rule, firewall, revoke token).
3. Rotate ngay secret liên quan.
4. Thu thập chứng cứ:
   - Audit log (`audit_logs` table)
   - API gateway access/error logs
   - Application logs có `request_id`
5. Đánh giá blast radius và dữ liệu bị ảnh hưởng.
6. Thực hiện remediation và rollback nếu cần.
7. Ghi postmortem và action items phòng ngừa tái diễn.

## 5) Audit Log Truy vết

Hệ thống ghi các action auth/admin vào bảng `audit_logs` với:

- actor (`actor_user_id`, `actor_email`, `actor_role`)
- action (`auth.*`, `admin.*`)
- request context (`request_id`, `method`, `path`, `ip_address`, `user_agent`)

Query mẫu:

```sql
SELECT id, created_at, actor_email, action, target_type, target_id, request_id
FROM audit_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY id DESC;
```
