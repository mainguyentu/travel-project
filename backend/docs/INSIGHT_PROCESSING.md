# INSIGHT_PROCESSING

Tài liệu này mô tả quy trình tạo và cập nhật insight cho destination trong backend hiện tại.

## 1) Mục tiêu

- Chuẩn hóa cách tính insight từ rating/comment.
- Cập nhật nhanh theo cơ chế incremental, không quét lại toàn bộ lịch sử rating.
- Giảm nhiễu khi dữ liệu còn ít bằng confidence blending.

## 2) Điểm chạm trong codebase

- Khởi tạo insight khi tạo destination:
  - `app/services/destinations.py`
  - `InsightService.initialize_for_destination(...)`
- Cập nhật insight khi user upsert rating:
  - `app/services/interaction.py`
  - `InsightService.apply_rating_update(...)`
- Logic insight chính:
  - `app/services/insight.py`
- Schema cache:
  - `app/db/models.py` (`DestinationInsight.insight_cache`)
  - Alembic revision `0004_destination_insight_cache`

## 3) Cấu trúc dữ liệu insight

Mỗi destination có một bản ghi trong `destination_insights`, gồm các phần chính:

- `score_snapshot`: điểm chi tiết theo dimension.
  - `scenery`
  - `accessibility`
  - `crowd`
  - `value`
- `human_override`: mức phân loại cho UI.
  - `*_level`: `low`, `medium`, `high`
- `final_data`: dữ liệu tổng hợp phục vụ hiển thị.
  - `score`
  - `summary`
  - `highlights`
  - `risks`
  - `recommendation`
  - `status`: `insufficient_data`, `low_confidence`, `reliable`
- `insight_cache`: dữ liệu trung gian để cập nhật O(1).

## 4) Luồng khởi tạo khi tạo destination

Khi tạo destination mới, hệ thống tạo insight nền với baseline:

- `BASELINE_SCORE = 50`
- `score_snapshot` khởi tạo 50 cho mọi dimension.
- `human_override` khởi tạo mức `medium`.
- `final_data.score` khởi tạo 50.
- `final_data.status` khởi tạo `insufficient_data`.
- `insight_cache` khởi tạo tổng/counter bằng 0.

## 5) Luồng cập nhật khi có rating

Khi user gửi hoặc cập nhật rating:

1. Lấy bản ghi rating cũ (nếu có) để tính delta đúng.
2. Chuẩn hóa comment và đánh giá contribution theo dimension.
3. Loại bỏ hoặc giảm trọng số comment không đạt chất lượng.
4. Trừ contribution cũ, cộng contribution mới vào `insight_cache`.
5. Tính lại `score_snapshot`, `human_override`, `final_data`.

## 6) Tiền xử lý và lọc chất lượng comment

Backend áp dụng các bước bảo vệ dữ liệu:

- Token hóa và chuẩn hóa chữ thường.
- Nhận diện spam mẫu:
  - ký tự lặp quá dài
  - từ lặp quá dày
  - chỉ ký tự đặc biệt
  - quảng cáo/số điện thoại/link
- Comment quá ngắn hoặc ít tín hiệu có thể bị giảm trọng số.
- Có xử lý phủ định đơn giản (ví dụ cụm có từ phủ định trước từ cảm xúc).

## 7) Tính điểm theo dimension

- Điểm rating được chuẩn hóa về thang 100.
- Contribution phụ thuộc vào:
  - rating chuẩn hóa
  - sentiment weight từ comment
  - dimension keyword match
- Điểm mỗi dimension được chặn trong khoảng 0..100.

## 8) Confidence blending

Để tránh điểm tổng bị lệch khi dữ liệu còn ít:

- Tính confidence theo số lượng review hợp lệ.
- Trộn điểm thực với baseline 50 theo confidence.

Hệ quả trực tiếp:

- Ít review: điểm tổng gần baseline hơn.
- Nhiều review: điểm tổng phản ánh dữ liệu thực mạnh hơn.

## 9) Phân loại trạng thái dữ liệu

`final_data.status` được dùng để biểu thị độ tin cậy:

- `insufficient_data`: dữ liệu quá ít.
- `low_confidence`: có dữ liệu nhưng chưa đủ dày.
- `reliable`: đủ dữ liệu để tin cậy hơn.

## 10) Quan hệ với API

Endpoint chi tiết destination trả trực tiếp dữ liệu insight:

- `GET /api/v1/destinations/{destination_id}`
- Trường trả về gồm `insight` và `metrics`.

Điều này cho phép frontend render popup chi tiết với dữ liệu tổng hợp mà không cần gọi thêm endpoint phụ.

## 11) Testing liên quan

Các test insight hiện có tại:

- `backend/tests/test_insight.py`

Các test này bao phủ:

- baseline initialization
- cập nhật cache và score theo rating
- xử lý comment ngắn/spam

## 12) Ghi chú vận hành

- Insight được cập nhật trong transaction của nghiệp vụ rating, nên cần theo dõi lỗi DB/transaction ở service interaction.
- Khi thay đổi thuật toán trong `app/services/insight.py`, cần cập nhật đồng thời:
  - test insight
  - API reference (nếu có thay đổi contract)
  - tài liệu này
