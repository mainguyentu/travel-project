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
* **Lọc nội dung**: Bỏ qua các review < 5 chữ hoặc chứa spam pattern (xem Phụ lục VII).
* **Chuẩn hoá điểm**:
    $$normalized\_score = \left( \frac{rating\_score}{5} \right) \times 100$$

### 2. Phân loại Keyword & Sentiment (Nâng cấp quan trọng)
Hệ thống sử dụng **hybrid approach**: Bộ từ khóa mở rộng + Rule-based sentiment + xử lý ngữ cảnh (negation, intensity, irony cơ bản). Khuyến nghị kết hợp model NLP (PhoBERT hoặc tương đương) nếu có thể.

**Bảng từ khóa mở rộng (tiêu biểu):**

| Khía cạnh     | Keywords tiêu biểu |
|---------------|--------------------|
| **Scenery**   | đẹp, view, phong cảnh, chill, biển, núi, sống ảo, hùng vĩ, hoang sơ, thiên nhiên, check-in, instagram, bức tranh, cảnh quan |
| **Accessibility** | dễ đi, khó đi, xa, đường, xe, di chuyển, gần trung tâm, đường xấu, đèo dốc, xe máy, grab, phượt, đường bộ |
| **Crowd**     | đông, vắng, chen, quá tải, chen chúc, ít người, vắng vẻ, peak season, cuối tuần đông, đông vui, đông chán |
| **Value**     | giá, đắt, rẻ, phí, dịch vụ, xứng đáng, tiền nào của nấy, phí vào cửa, ăn uống đắt, chất lượng dịch vụ, đáng tiền |

**Trọng số sắc thái (Sentiment Weight) nâng cấp:**
* **Positive**: +1 (cơ bản), +1.5 (rất, cực kỳ), +2 (siêu, tuyệt vời).
* **Negative**: -1 (cơ bản), -1.5 (khá, hơi nhiều), -2 (cực kỳ, quá tệ).
* **Neutral**: +0.3.
* **Negation & Context**: "không", "chưa", "ít", "nhưng" (xử lý "đông nhưng vui", "đắt nhưng đáng tiền", "khó đi nhưng view đẹp").
* **Intensity & Irony**: Phát hiện cường độ từ ("hơi", "cực kỳ") và một số trường hợp irony (rating cao nhưng toàn từ tiêu cực → giảm weight).

**Xử lý nâng cao**: 
- Phân tích theo câu (sentence-level).
- Mỗi review chỉ góp tối đa **1 lần** cho mỗi dimension (tránh bias từ review dài spam keyword).

### 3. Công thức tính điểm Dimension (Nâng cấp)
$$score\_dimension = \text{clamp} \left( \frac{\sum (normalized\_score \times sentiment\_weight \times review\_weight)}{number\_of\_reviews\_mentioning\_dimension}, 0, 100 \right)$$

**Bổ sung review_weight**:
- Time decay: Review > 24 tháng → multiplier giảm dần (0.7~0.9).
- Reviewer quality: User có nhiều review chất lượng → weight cao hơn.

---

## III. Phân cấp Mức độ (Human Override)

Dựa trên `score_snapshot`, phân loại các mức độ để hiển thị nhãn (label):
* **Low**: Score < 40
* **Medium**: 40 ≤ Score < 70
* **High**: Score ≥ 70

---

## IV. Tổng hợp dữ liệu cuối cùng (Final Data)

### 1. Điểm tổng kết (Final Score) — Nâng cấp
Sử dụng **trọng số động (dynamic weighting)** theo loại destination:

- **Mặc định**: Scenery (35%), Accessibility (25%), Value (25%), Crowd (15%).
- **Biển/Phong cảnh tự nhiên**: Scenery 45%, Crowd 10%.
- **Điểm check-in đô thị**: Accessibility 35%, Value 30%.
- **Di tích văn hóa**: Value (trải nghiệm) tăng, Scenery giảm nhẹ.

$$final\_score = (scenery \times w1) + (accessibility \times w2) + (value \times w3) + (crowd \times w4)$$

Cho phép admin override trọng số cho từng category.

### 2. Logic nội dung tự động (Nâng cấp)
* **Summary**: Sử dụng template đa điều kiện (ưu tiên kết hợp 2-3 dimension):
    * Scenery ≥ 80 và Crowd ≥ 60 → `"Phong cảnh tuyệt đẹp, dù đôi khi đông nhưng vẫn rất đáng trải nghiệm."`
    * Crowd < 40 và Accessibility < 50 → `"Vắng vẻ nhưng di chuyển khó khăn, phù hợp phượt thủ hoặc người thích yên tĩnh."`
    * Scenery > 70 và Value > 60 → `"Địa điểm có phong cảnh đẹp và giá trị trải nghiệm tốt."`
    * Còn lại: `"Địa điểm ở mức trung bình, phù hợp trải nghiệm cơ bản."`
* **Highlights**: Thêm nếu dimension ≥ 70 **và** confidence đủ cao. Ưu tiên unique keyword frequency cao (ví dụ: nhiều "sống ảo" → "Rất lý tưởng để sống ảo và chụp ảnh").
* **Risks**: Thêm nếu dimension < 40. Tránh hiển thị mạnh khi confidence thấp.
* **Recommendation**:
    * `final_score` ≥ 75: "Rất đáng đi"
    * `final_score` ≥ 60: "Có thể trải nghiệm"
    * Còn lại: "Cân nhắc trước khi đi"
  → Có thể bổ sung theo đối tượng (gia đình, cặp đôi, solo) nếu có dữ liệu reviewer.

**Bổ sung**: Seasonal note nếu phát hiện pattern theo thời gian (ví dụ: "Đông đúc nhất vào mùa hè và dịp lễ").

---

## V. Độ tin cậy & Xử lý dữ liệu thiếu (Nâng cấp)

**Confidence Score** cải tiến:
$$confidence = \min \left( 1, \frac{total\_reviews}{50} \times diversity\_factor \times recency\_factor \right)$$
- `diversity_factor`: Cao hơn nếu review từ nhiều user khác nhau.
- `recency_factor`: Tỷ lệ review trong 12 tháng gần nhất.

**Công thức pha trộn (Blended Score):**
$$final\_score = (real\_data\_score \times confidence) + (baseline\_score \times (1 - confidence))$$
- `baseline_score`: **Dynamic** — dùng trung bình của các destination cùng loại/tỉnh thay vì cố định 50.

**Phân loại trạng thái dữ liệu (`status`)**:
* `< 3 reviews`: `insufficient_data`
* `< 10 reviews`: `low_confidence`
* `>= 10 reviews`: `reliable`
* **Bổ sung**: `high_variance` nếu các dimension chênh lệch quá lớn (cảnh báo "Ý kiến du khách trái chiều").

---

## VI. Tối ưu hiệu suất (Performance)

Để đảm bảo tốc độ phản hồi $O(1)$, hệ thống sử dụng cơ chế **Insight Cache**. Không quét lại toàn bộ database khi có rating mới.

**Mẫu Cache** (giữ nguyên nhưng cần mở rộng để lưu thêm sum_weighted, count_reviews_mentioning, last_update...).

**Khi có review mới**: Cập nhật incremental + áp dụng time decay cho dữ liệu cũ nếu cần.

---

## VII. Phụ lục: Gợi ý Spam Pattern (Nâng cấp)
Các mẫu cần loại bỏ tự động để đảm bảo tính khách quan của Insight:
1. **Ký tự lặp lại**: "đẹp quáaaaaaaaaa", ".........."
2. **Từ vô nghĩa/Quảng cáo**: "ib nhận link", "liên hệ số điện thoại 09...", "rác", "123456".
3. **Copy-paste**: Các đoạn văn bản giống hệt nhau từ các user khác nhau.
4. **Review không liên quan**: Chỉ chứa emoji hoặc các từ cảm thán không có keyword khía cạnh.
5. **Review bombing**: Một user đăng nhiều review giống nhau trong thời gian ngắn.
6. **Fake review nghi ngờ**: Văn phong quảng cáo mạnh, ngôn ngữ không tự nhiên, hoặc review chỉ toàn positive cực đoan mà không có chi tiết.

**Bổ sung**: Kiểm tra language consistency và flag review có dấu hiệu giả mạo.

---

**Ghi chú triển khai**:
- Ưu tiên giai đoạn 1: Cải thiện phần Keyword & Sentiment Analysis.
- Giai đoạn 2: Dynamic weighting + Blended score nâng cao.
- Giai đoạn 3: Logic nội dung thông minh + seasonal/context.

File này đã được cập nhật toàn diện hơn, giảm rủi ro insight generic hoặc sai lệch. 