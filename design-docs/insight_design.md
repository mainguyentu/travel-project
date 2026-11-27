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

### 3. Công thức tính điểm Dimension
$$score\_dimension = \text{clamp} \left( \frac{\sum (normalized\_score \times sentiment\_weight)}{total\_mentions}, 0, 100 \right)$$

---

## III. Phân cấp Mức độ (Human Override)

Dựa trên `score_snapshot`, phân loại các mức độ để hiển thị nhãn (label):
* **Low**: Score < 40
* **Medium**: 40 $\le$ Score < 70
* **High**: Score $\ge$ 70

---

## IV. Tổng hợp dữ liệu cuối cùng (Final Data)

### 1. Điểm tổng kết (Final Score)
Sử dụng phương pháp bình quân gia quyền để ưu tiên các yếu tố quan trọng:
* **Trọng số:** Scenery (35%), Accessibility (25%), Value (25%), Crowd (15%).

$$final\_score = (scenery \times 0.35) + (accessibility \times 0.25) + (value \times 0.25) + (crowd \times 0.15)$$

### 2. Logic nội dung tự động
* **Summary**: 
    * Nếu `scenery > 70` và `value > 60`: "Địa điểm có phong cảnh đẹp và giá trị trải nghiệm tốt."
    * Nếu `crowd < 40`: "Địa điểm khá đông đúc, cần cân nhắc thời gian ghé thăm."
    * Còn lại: "Địa điểm ở mức trung bình, phù hợp trải nghiệm cơ bản."
* **Highlights**: Thêm vào danh sách nếu điểm của dimension > 70 (ví dụ: "Phong cảnh đẹp", "Dễ di chuyển").
* **Risks**: Thêm vào danh sách nếu điểm của dimension < 40 (ví dụ: "Chi phí cao", "Khó tiếp cận").
* **Recommendation**:
    * `final_score >= 75`: "Rất đáng đi"
    * `final_score >= 60`: "Có thể trải nghiệm"
    * Còn lại: "Cân nhắc trước khi đi"

---

## V. Độ tin cậy & Xử lý dữ liệu thiếu

Để tránh sai lệch khi có quá ít đánh giá, áp dụng **Confidence Score**:
$$confidence = \min \left( 1, \frac{total\_reviews}{50} \right)$$

**Công thức pha trộn (Blended Score):**
$$final\_score = (real\_data\_score \times confidence) + (baseline\_score \times (1 - confidence))$$
*(Trong đó `baseline_score` mặc định là 50).*

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
  "count_accessibility": 4
}
```
**Khi có review mới:** Chỉ cần lấy `sum` cũ + `(score * weight)` mới và `count` cũ + 1.

---

## VII. Phụ lục: Gợi ý Spam Pattern
Các mẫu cần loại bỏ tự động để đảm bảo tính khách quan của Insight:
1.  **Ký tự lặp lại**: "đẹp quáaaaaaaaaa", ".........."
2.  **Từ vô nghĩa/Quảng cáo**: "ib nhận link", "liên hệ số điện thoại 09...", "rác", "123456".
3.  **Copy-paste**: Các đoạn văn bản giống hệt nhau từ các user khác nhau.
4.  **Review không liên quan**: Chỉ chứa emoji hoặc các từ cảm thán không có keyword khía cạnh.