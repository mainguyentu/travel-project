# Production Gate Checklist

Checklist này là cổng chất lượng cuối cùng trước khi triển khai staging/prod.
Mục tiêu: quyết định rõ ràng **GO / NO-GO** dựa trên bằng chứng.

Cập nhật: 2026-04-24

## 1. Quy tắc pass/fail

- Chỉ được **GO** khi toàn bộ mục `Critical` đều pass.
- Mục `High` có thể chấp nhận tối đa 1 ngoại lệ, phải có owner + deadline + rollback plan.
- Mục `Medium` không chặn release nhưng bắt buộc tạo follow-up issue.

## 2. Gate Critical (bắt buộc pass)

- [ ] **Config/Secrets**
  - Không còn secret/default credential trong manifest deploy.
  - Dùng env file theo môi trường, không commit giá trị thật.
  - `RUN_SEED=false` cho staging/prod.
- [ ] **Database migration**
  - Migration chạy thành công trên môi trường tương tự production.
  - Có rollback hoặc forward-fix plan cho migration.
- [ ] **API contract compatibility**
  - Endpoint thay đổi đã được versioning hoặc backward compatible.
  - Contract tests pass cho auth/destination/interaction/admin/analytics.
- [ ] **Security baseline**
  - JWT secret đủ mạnh và đã rotate theo policy.
  - Không có lỗ hổng mức critical/high chưa xử lý.
  - CORS whitelist đúng môi trường release.
- [ ] **Observability**
  - Có request ID xuyên gateway -> services -> logs.
  - Health checks pass cho toàn bộ service.
  - Alert kênh on-call hoạt động (test alert đã xác nhận).
- [ ] **Release artifact**
  - Image tag immutable (không dùng `latest`).
  - Build provenance rõ ràng (commit SHA, release tag).

## 3. Gate High (khuyến nghị chặn nếu fail nhiều)

- [ ] **Performance baseline**
  - API p95/p99 nằm trong ngưỡng SLO đã công bố.
  - Không có truy vấn DB chậm mới vượt ngưỡng.
- [ ] **Data boundary compliance**
  - Không có truy cập chéo bảng ngoài ownership đã định nghĩa trong `DATA_BOUNDARY_DRAFT.md`.
  - Event contract mới có version + idempotency strategy.
- [ ] **Async pipeline readiness**
  - DLQ rỗng hoặc ở mức chấp nhận được.
  - Worker retry/backoff cấu hình đúng theo runbook.
- [ ] **Cache correctness**
  - Invalidation path đã test cho các luồng mutate quan trọng.
  - Không có stale-data bug đã biết ở critical flow.

## 4. Gate Medium (theo dõi sau release)

- [ ] **Docs completeness**
  - Cập nhật docs liên quan: `API_REFERENCE.md`, `ARCHITECTURE.md`, `DEPLOYMENT_RUNBOOK.md` (nếu có thay đổi).
- [ ] **Runbook readiness**
  - Có kịch bản incident phổ biến và người trực biết quy trình.
- [ ] **Technical debt capture**
  - TODO tạm thời đã có issue với mức ưu tiên và owner.

## 5. Evidence cần đính kèm trước khi GO

- [ ] Link pipeline CI/CD pass.
- [ ] Kết quả test (unit/integration/e2e) mới nhất.
- [ ] Ảnh/chụp hoặc log chứng minh health checks pass.
- [ ] Kết quả smoke test post-deploy trên staging.
- [ ] Danh sách thay đổi (release notes) và phạm vi ảnh hưởng.

## 6. Go/No-Go template

### Release
- Version/Tag:
- Commit SHA:
- Environment:
- Release owner:

### Gate summary
- Critical: `x/y` pass
- High: `x/y` pass
- Medium: `x/y` pass

### Decision
- [ ] GO
- [ ] NO-GO

### Open risks (nếu GO có ngoại lệ)
- Risk:
- Impact:
- Mitigation:
- Owner:
- Deadline:

### Rollback plan
- Trigger rollback khi:
- Cách rollback:
- Người quyết định rollback:

