# Quy trình Xử lý Insight cho Destination

Tài liệu này quy định logic tự động tạo và cập nhật thông tin chi tiết (insights) khi một địa điểm (destination) được thêm mới hoặc nhận được đánh giá (rating) từ người dùng.

## I. Cấu trúc dữ liệu (Data Schema)

Mỗi Destination Insight sẽ bao gồm 3 thành phần chính:

1.  **`score_snapshot`**: Chứa điểm số chi tiết của 4 khía cạnh:
    * `scenery` (Phong cảnh)
    * `accessibility` (Khả năng tiếp cận/Di chuyển)
    * `crowd` (Độ đông đúc)
    * `value` (Giá trị trải nghiệm/Giá cả)
2.  **`human_override`**: Phân loại mức độ hiển thị cho người dùng:
    * `scenery_level`, `accessibility_level`, `crowd_level`, `value_level` (Giá trị: `low`, `medium`, `high`).
3.  **`final_data`**: Dữ liệu tổng hợp cuối cùng:
    * `score`: Điểm tổng kết.
    * `summary`: Mô tả ngắn gọn.
    * `highlights`: Các điểm nổi bật (Ưu điểm).
    * `risks`: Các rủi ro (Nhược điểm).
    * `recommendation`: Lời khuyên trải nghiệm.
    * `status`: Trạng thái độ tin cậy của dữ liệu.

---

## II. Logic Tính toán Score

### 1. Chuẩn hoá dữ liệu đầu vào
Khi nhận một đánh giá, thực hiện các bước sau:
* **Lọc nội dung**: Bỏ qua các review < 5 chữ hoặc chứa spam pattern.
* **Chuẩn hoá điểm**:
    $$normalized\_score = \left( \frac{rating\_score}{5} \right) \times 100$$

### 2. Phân loại Keyword & Sentiment
Hệ thống sử dụng bộ từ khóa để xác định khía cạnh được nhắc đến và sắc thái (sentiment) của nó.

| Khía cạnh | Keywords tiêu biểu |
| :--- | :--- |
| **Scenery** | đẹp, view, phong cảnh, chill, biển, núi, sống ảo |
| **Accessibility** | dễ đi, khó đi, xa, đường, xe, di chuyển |
| **Crowd** | đông, vắng, chen, quá tải |
| **Value** | giá, đắt, rẻ, phí, dịch vụ |

**Trọng số sắc thái (Sentiment Weight):**
* **Positive (+1):** đẹp, tốt, ổn, rẻ, thuận tiện, dễ, rất đẹp (+1.5).
* **Negative (-1):** đông, đắt, khó, tệ, xa, chật, cực kỳ đông (-1.5).
* **Neutral (+0.3):** Các trường hợp không chứa từ cảm xúc rõ rệt.
* **Negation (Đảo chiều):** "không", "chưa", "ít" (Ví dụ: "không đông" sẽ chuyển từ Negative sang Positive).

**[NÂNG CẤP]** **Phân tích sâu ngữ nghĩa (Aspect-Based Sentiment Analysis)**
- Để xử lý câu phức tạp (ví dụ: "phong cảnh đẹp nhưng đường xa"), hệ thống sử dụng mô hình **phoBERT** tinh chỉnh cho tác vụ ABSA, gán sentiment riêng cho từng khía cạnh trong cùng một câu.
- **Phủ định mở rộng**: Nhận diện các cấu trúc như "không đẹp lắm", "chưa hẳn đã xấu", "chẳng có gì hay" thông qua phân tích phụ thuộc (dependency parsing).

**[BỔ SUNG]** **Hệ số điều chỉnh từ độ tin cậy người dùng (User Reputation)**
- Mỗi review được nhân với hệ số `user_factor = min(1.5, 0.8 + 0.2 * reputation_score)`, trong đó `reputation_score` chuẩn hóa dựa trên số lượng review đã đóng góp, tỷ lệ được vote hữu ích và thời gian tham gia.

**[BỔ SUNG]** **Hệ số nhất quán văn bản – số sao**
- Nếu sentiment tổng thể của văn bản (positive/negative/neutral) mâu thuẫn với số sao (1-2 → negative, 4-5 → positive), review bị giảm trọng số còn 0.5 lần.

**[BỔ SUNG]** **Hệ số chất lượng nội dung**
- Review dài > 50 từ, có ≥2 khía cạnh được nhắc đến: thưởng hệ số `1 + 0.1 * log(length/50)`, tối đa 1.3.

### 3. Công thức tính điểm Dimension
$$score\_dimension = \text{clamp} \left( \frac{\sum (normalized\_score \times sentiment\_weight \times user\_factor \times consistency\_factor \times content\_factor \times image\_factor)}{\sum (1 \times \text{hệ số tương ứng})}, 0, 100 \right)$$

**[BỔ SUNG]** **Suy giảm theo thời gian (Time Decay)**
- Trọng số của mỗi review giảm theo hàm mũ: `weight = base_weight * exp(-λ * months_since_review)` với λ được chọn sao cho sau 12 tháng trọng số còn 50%.

---

## III. Phân cấp Mức độ (Human Override)

Dựa trên `score_snapshot`, phân loại các mức độ để hiển thị nhãn (label):
* **Low**: Score < 40
* **Medium**: 40 $\le$ Score < 70
* **High**: Score $\ge$ 70

---

## IV. Tổng hợp dữ liệu cuối cùng (Final Data)

### 1. Điểm tổng kết (Final Score)
**[NÂNG CẤP]** Sử dụng trọng số động theo danh mục địa điểm (category):
* **Biển/Đảo**: Scenery (40%), Accessibility (20%), Value (25%), Crowd (15%)
* **Núi/Cao nguyên**: Scenery (35%), Accessibility (25%), Value (25%), Crowd (15%)
* **Thành phố/Bảo tàng**: Scenery (20%), Accessibility (35%), Value (25%), Crowd (20%)
* **Mặc định**: Scenery (35%), Accessibility (25%), Value (25%), Crowd (15%)

$$final\_score = \sum_{dim} (score_{dim} \times weight_{category}(dim))$$

### 2. Logic nội dung tự động
**[NÂNG CẤP]** Sử dụng template đa dạng hơn (tối thiểu 10 mẫu) và kết hợp với phân vị để tránh lặp.

* **Summary**: Chọn mẫu dựa trên tổ hợp các mức `low/medium/high` của 4 khía cạnh. Ví dụ:
    * "Phong cảnh tuyệt vời, dễ di chuyển nhưng hơi đông và giá cả hợp lý."
    * "Điểm đến yên tĩnh với chi phí phải chăng, phù hợp nghỉ dưỡng."

* **Highlights**: Thêm nếu điểm của khía cạnh ≥ **percentile 70** của cùng category.
* **Risks**: Thêm nếu điểm của khía cạnh ≤ **percentile 30** của cùng category.

* **Recommendation**:
    * `final_score >= 75`: "Rất đáng đi"
    * `final_score >= 60`: "Có thể trải nghiệm"
    * Còn lại: "Cân nhắc trước khi đi"

**[BỔ SUNG]** **Insight theo mùa/thời điểm**
- Hệ thống tự động phân cụm review theo khoảng thời gian (theo mùa, ngày lễ, cuối tuần) và cung cấp insight riêng biệt khi người dùng truy vấn theo thời gian cụ thể.

---

## V. Độ tin cậy & Xử lý dữ liệu thiếu

Để tránh sai lệch khi có quá ít đánh giá, áp dụng **Confidence Score**:
$$confidence = \min \left( 1, \frac{total\_reviews}{50} \right)$$

**Công thức pha trộn (Blended Score):**
$$final\_score = (real\_data\_score \times confidence) + (baseline\_score \times (1 - confidence))$$
*(Trong đó `baseline_score` mặc định là 50).*

**[NÂNG CẤP]** **Baseline động theo category**
- `baseline_score` được lấy là điểm trung bình của tất cả địa điểm cùng category (hoặc cùng khu vực) thay vì cố định 50.

**Phân loại trạng thái dữ liệu (`status`):**
* `< 3 reviews`: `insufficient_data`
* `< 10 reviews`: `low_confidence`
* `>= 10 reviews`: `reliable`

---

## VI. Tối ưu hiệu suất (Performance)

Để đảm bảo tốc độ phản hồi $O(1)$, hệ thống sử dụng cơ chế **Insight Cache**. Không quét lại toàn bộ database khi có rating mới.

**Mẫu Cache:**
```json
{
  "sum_scenery": 450,
  "count_scenery": 5,
  "sum_accessibility": 320,
  "count_accessibility": 4,
  "last_decay_update": "2025-04-16T00:00:00Z"
}
```

**Khi có review mới**: Chỉ cần lấy `sum` cũ + `(score * weight * time_decay)` mới và count cũ + 1.
**Cập nhật định kỳ**: Hàng ngày áp dụng hàm suy giảm thời gian cho các sum đã lưu.

## VII. Phụ lục: Gợi ý Spam Pattern
Các mẫu cần loại bỏ tự động để đảm bảo tính khách quan của Insight:

**Ký tự lặp lại**: `"đẹp quáaaaaaaaaa", ".........."`

**Từ vô nghĩa/Quảng cáo**: `"ib nhận link", "liên hệ số điện thoại 09...", "rác", "123456"`.

**Copy-paste**: Các đoạn văn bản giống hệt nhau từ các user khác nhau.

**Review không liên quan**: Chỉ chứa emoji hoặc các từ cảm thán không có keyword khía cạnh.

## [NÂNG CẤP] Phát hiện spam nâng cao

Sử dụng mô hình LSTM được huấn luyện trên tập dữ liệu spam thực tế để phát hiện các mẫu tinh vi hơn (quảng cáo trá hình, nội dung lặp mờ).


## VIII. Bổ sung: Các điều kiện mới (đã tích hợp vào công thức ở phần II và IV)


| Điều kiện | Mục đích | Cách áp dụng
| :--- | :--- | :--- |
| **User Reputation** | Tăng độ tin cậy | 	Nhân trọng số sentiment với hệ số uy tín.
| **Tính nhất quán văn bản – số sao** | Phát hiện review bất thường | Giảm trọng số hoặc bỏ qua review nếu mâu thuẫn.
| **Thời gian review (Recency)** | Ưu tiên thông tin mới | Trọng số giảm theo hàm mũ của thời gian.
| **Chất lượng nội dung & ảnh** | Khuyến khích đánh giá chi tiết | Thưởng hệ số nhân vào trọng số sentiment.
| **Ngưỡng động theo category** | Đánh giá tương đối chính xác hơn | Thay thế ngưỡng tuyệt đối 70/40 bằng percentile.
| **Cá nhân hóa (tùy chọn)** | Phù hợp sở thích người dùng | Điều chỉnh trọng số tạm thời khi có profile người dùng (ví dụ: tăng trọng `crowd` nếu thích yên tĩnh).