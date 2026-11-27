# Destination Image Migration Plan (Cloudinary)

## 1. Understanding Summary
- Mở rộng chức năng xử lý ảnh cho destination: không lưu trực tiếp URL gốc từ payload như hiện tại.
- Hệ thống sẽ tải ảnh từ URL nguồn, upload lên Cloudinary, sau đó thay URL ảnh bằng URL Cloudinary.
- Áp dụng cho toàn bộ luồng ghi dữ liệu: create, bulk create, update.
- Áp dụng cho toàn bộ dữ liệu cũ trong DB bằng cơ chế backfill.
- Nếu URL lỗi hoặc upload lỗi: fallback giữ nguyên URL gốc và ghi log lỗi theo cơ chế logging hiện có.
- Upload dùng Cloudinary signed upload từ backend.
- Backfill chạy nền theo batch nhỏ, có checkpoint/resume, giới hạn tốc độ.

## 2. Scope
- In scope:
  - POST admin destinations (single create)
  - POST admin destinations bulk
  - PUT admin destinations update
  - Backfill toàn bộ dữ liệu destination hiện có
- Out of scope:
  - Thay đổi giao diện admin để upload file trực tiếp từ client
  - Chuyển đổi provider sang AWS S3 trong giai đoạn này

## 3. Assumptions
- Cloudinary credentials được cấu hình qua biến môi trường backend.
- URL trả về dùng secure_url từ Cloudinary.
- Hệ thống logging hiện có hỗ trợ structured logging theo context URL lỗi.
- Cần giữ compatibility API hiện tại với các trường img_url và img_urls.
- Nếu img_urls có dữ liệu, img_url sẽ luôn bằng phần tử đầu tiên của img_urls.

## 4. Constraints and Non-Functional Requirements
- Performance:
  - Backfill chạy batch 50 destination/lần.
  - Upload concurrency nhẹ (mặc định 3-5).
  - Timeout cho download/upload để tránh treo job.
- Reliability:
  - Không fail toàn request khi lỗi 1 URL ảnh.
  - Idempotent: URL đã migrate thì skip.
  - Backfill có checkpoint để resume sau restart/lỗi.
- Security:
  - Signed upload only.
  - Không log secrets hoặc credentials.
- Observability:
  - Log theo từng URL lỗi: destination_id, source_url, error_reason, stage.
  - Log tổng kết theo batch: processed, migrated, skipped, fallback.
- Maintainability:
  - Tách module xử lý storage ảnh độc lập, service gọi qua interface ổn định.

## 5. Chosen Design Approach
Approach A (recommended):
- In-line migration cho luồng ghi mới (create, bulk, update).
- Worker/job riêng cho backfill toàn bộ dữ liệu cũ.
- Fallback per-URL giữ dữ liệu nghiệp vụ không bị gián đoạn.

Lý do chọn:
- Đủ nhanh để triển khai.
- Không làm vỡ contract API hiện tại.
- Rủi ro thấp cho hệ thống hiện hữu.
- Có đường nâng cấp dần sang event-driven nếu traffic tăng.

## 6. Architecture and Components
### 6.1 Image storage module
Thêm module backend (ví dụ: services hoặc utils chuyên biệt) với trách nhiệm:
- Validate và normalize URL ảnh đầu vào.
- Download ảnh nguồn với timeout, giới hạn size.
- Upload signed lên Cloudinary.
- Trả về secure_url hoặc fallback URL gốc khi lỗi.
- Ghi structured log cho các lỗi theo từng URL.

### 6.2 Integration points
- DestinationService:
  - Hook vào sau bước normalize dữ liệu ảnh hiện tại.
  - Áp dụng cho create, create_many, update.
- Backfill worker/job:
  - Quét dữ liệu destination theo id tăng dần.
  - Chạy pipeline migrate giống luồng online.
  - Cập nhật DB và checkpoint theo batch.

### 6.3 Data fields behavior
- Input hỗ trợ như hiện tại: img_url, img_urls, image.
- Output lưu DB:
  - img_urls: danh sách URL sau migrate/fallback.
  - img_url: phần tử đầu img_urls hoặc null.
- Không thay đổi schema response API để tránh ảnh hưởng frontend hiện tại.

## 7. Data Flow
### 7.1 Online flow (create/bulk/update)
1. Nhận payload.
2. Normalize dữ liệu ảnh thành list URL.
3. Duyệt từng URL:
   - Nếu đã là Cloudinary URL: skip.
   - Nếu chưa migrate: download + upload signed + lấy secure_url.
   - Nếu lỗi: log + giữ URL gốc.
4. Đồng bộ lại img_urls và img_url.
5. Lưu destination.

### 7.2 Backfill flow
1. Đọc checkpoint hiện tại.
2. Query 50 destination tiếp theo.
3. Chạy migrate pipeline cho từng destination.
4. Commit theo batch.
5. Ghi checkpoint mới.
6. Lặp đến khi hết dữ liệu.

## 8. Error Handling Policy
- Lỗi ở từng URL không fail toàn destination.
- URL lỗi giữ nguyên bản gốc.
- Tất cả lỗi ghi log có context để replay/điều tra.
- Nếu lỗi hệ thống (DB down, config thiếu) thì dừng batch và giữ checkpoint trước đó.

## 9. Testing Strategy
- Unit tests:
  - Upload thành công trả secure_url.
  - URL đã Cloudinary thì skip.
  - Lỗi download/upload thì fallback và log.
  - Đồng bộ img_url và img_urls đúng.
- Integration tests:
  - Create/bulk/update giữ đúng behavior API.
  - Fallback không làm fail request toàn cục.
- Backfill tests:
  - Batch size 50 đúng.
  - Resume từ checkpoint đúng.
  - Idempotent khi chạy lại.

## 10. Rollout Plan
1. Bật feature flag cho xử lý ảnh Cloudinary ở luồng online.
2. Deploy staging, xác minh log và dữ liệu URL.
3. Deploy production, bật online flow trước.
4. Chạy backfill production theo batch 50.
5. Theo dõi lỗi và metric batch; rerun an toàn nếu cần.

## 11. Decision Log
1. Chuyển provider lưu ảnh sang Cloudinary.
   - Alternatives: AWS S3.
   - Reason: blocker setup/payment S3 ở giai đoạn hiện tại.
2. Dùng signed upload từ backend.
   - Alternatives: unsigned preset.
   - Reason: bảo mật và kiểm soát tốt hơn.
3. Fallback giữ URL gốc khi lỗi từng URL.
   - Alternatives: fail-fast hoặc drop URL lỗi.
   - Reason: không gián đoạn nghiệp vụ, vẫn có log để xử lý sau.
4. Áp dụng toàn bộ luồng online và toàn bộ dữ liệu cũ.
   - Alternatives: chỉ dữ liệu mới.
   - Reason: đảm bảo nhất quán dữ liệu toàn hệ thống.
5. Backfill batch 50 destination/lần + checkpoint/resume.
   - Alternatives: one-shot nhanh.
   - Reason: an toàn vận hành và phục hồi tốt.

## 12. Risks and Mitigations
- Risk: URL nguồn chết hoặc anti-hotlink.
  - Mitigation: fallback URL gốc + log + khả năng rerun.
- Risk: Latency tăng ở create/update.
  - Mitigation: timeout ngắn, concurrency giới hạn, theo dõi metric.
- Risk: Upload trùng.
  - Mitigation: nhận diện URL đã Cloudinary để skip.
- Risk: Mất checkpoint khi restart.
  - Mitigation: persist checkpoint sau mỗi batch commit.

## 13. Exit Criteria
- Understanding lock đã được user xác nhận.
- Design approach đã được user đồng ý.
- Assumptions và major risks đã được ghi rõ.
- Decision log đầy đủ cho toàn bộ quyết định chính.
