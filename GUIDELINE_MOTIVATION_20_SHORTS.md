# 🚀 CHIẾN LƯỢC & QUY TRÌNH SẢN XUẤT 20 YOUTUBE SHORTS VIRAL
## Mục tiêu: 1.000 Subscribers & 3.000.000 Views · Kênh Thảo Dương TV (@tuanweb2015)

Tài liệu này hướng dẫn chi tiết toàn bộ chiến lược, kịch bản, và cách vận hành các script Terminal tự động hóa trên nhánh `feature/motivation-20-shorts`.

---

## 📌 1. Phân Tích Thực Chiến Từ Video Đạt 1.4K Views

Trên kênh YouTube Thảo Dương TV, video ngắn đạt hiệu quả cao nhất vừa qua là:
* **Tiêu đề:** *"5 Phút Sáng Quyết Định Năng Suất Cả Ngày"*
* **Lượt xem:** 1.428 views
* **Tỷ lệ giữ chân (Retention):** **96,1%** (Thời lượng xem trung bình 14s/15s)

### 🔑 4 Yếu Tố Tạo Nên Thành Công:
1. **Hook có con số và thời gian cụ thể:** `"5 Phút Sáng"` đánh trúng tâm lý người xem muốn giải pháp nhanh, thực tế.
2. **Thời lượng vàng (12s – 24s):** Người xem xem hết 100% video ngay lần lướt đầu tiên, kích hoạt thuật toán YouTube đề xuất mạnh vào feed Shorts.
3. **Chủ đề Năng lượng sống / Phát triển bản thân:** Nhu cầu người xem tìm kiếm sự bình an, động lực, yêu đời và năng suất rất lớn.
4. **CTA kêu gọi tự nhiên:** Lời kêu gọi đăng ký kênh chân thành, ấm áp theo phong cách Thảo Dương TV.

---

## 🎯 2. Chiến Lược 20 Video Mới (Chia Thành 4 Nhóm Chủ Đề)

| Nhóm | Số lượng | Chủ đề chính | Mục tiêu chuyển đổi |
| :--- | :---: | :--- | :--- |
| **Nhóm 1 (Bài 1 - 5)** | 5 | **Năng lượng buổi sáng & Năng suất** | Kéo view đỉnh điểm vào khung giờ 06:30 - 07:30 sáng |
| **Nhóm 2 (Bài 6 - 10)** | 5 | **Tư duy tích cực & Yêu đời** | Tạo cảm xúc chữa lành, an vui, tỷ lệ like & share cao |
| **Nhóm 3 (Bài 11 - 15)** | 5 | **Sống có ích cho gia đình & Xã hội** | Chạm tới tình cảm gia đình, lòng biết ơn, kích thích comment |
| **Nhóm 4 (Bài 16 - 20)** | 5 | **Sáng tạo & Phát triển bản thân** | Khơi dậy kỷ luật, hành động, tăng subscriber trung thành |

---

## 📂 3. Cấu Trúc File & Script Trên Nhánh Này

* `data/motivation_20_shorts.json`: Cơ sở dữ liệu chứa đầy đủ 20 kịch bản, tiêu đề chuẩn `#Shorts`, hook, hashtags, và phần miêu tả chuẩn SEO.
* `batch_render_motivation.py`: Công cụ Terminal dựng video hàng loạt hoặc đơn lẻ (tự động tạo frame ảnh, TTS giọng Hoài Mỹ miền Nam, mix nhạc zen tĩnh lặng, ghép file MP4 dọc 720x1280).
* `static/output/motivation_short_01.mp4`: Video mẫu số 1 đã dựng thành phẩm.
* `GUIDELINE_MOTIVATION_20_SHORTS.md`: Bản tài liệu hướng dẫn này.

---

## 💻 4. Hướng Dẫn Chạy Terminal Scripts (Manual Run)

Mọi thao tác đều có thể chủ động chạy thủ công bằng Terminal trên máy Mac của bạn.

### Bước 1: Mở Terminal và chuyển vào thư mục dự án
```bash
cd /Users/abc/.gemini/antigravity/scratch/tiktok_nikaya
```

### Bước 2: Kiểm tra hoặc chuyển sang nhánh feature
```bash
git checkout feature/motivation-20-shorts
```

### Bước 3: Lệnh Dựng Video (Batch Render)

* **Cách 1: Render 1 video đơn lẻ để kiểm tra (ví dụ bài số 2):**
  ```bash
  python3 batch_render_motivation.py 2
  ```

* **Cách 2: Render một dải video (ví dụ từ bài 1 đến bài 5):**
  ```bash
  python3 batch_render_motivation.py 1 5
  ```

* **Cách 3: Render trọn bộ cả 20 video tự động:**
  ```bash
  python3 batch_render_motivation.py all
  ```

*Tất cả video sau khi render sẽ xuất hiện tại thư mục:* `static/output/motivation_short_XX.mp4`

---

## ⏰ 5. Lịch Trình Đăng Bài Khuyên Dùng (Khung Giờ Vàng YouTube)

Để đạt mục tiêu 3 triệu views và 1.000 subscribers, không nên đăng dồn dập 20 video cùng 1 lúc mà nên đăng rải đều theo lịch trình:

* **Tần suất tối ưu:** **3 video / ngày** (liên tục trong 7 ngày)
* **Khung giờ vàng phân phối Shorts:**
  1. **Khung Sáng (06:30 – 07:30):** Đăng các video thuộc *Nhóm 1: Năng lượng buổi sáng*
  2. **Khung Trưa (11:30 – 12:30):** Đăng các video thuộc *Nhóm 2 & 3: Yêu đời / Gia đình*
  3. **Khung Tối (19:30 – 21:00):** Đăng các video thuộc *Nhóm 4: Phát triển bản thân & Kỷ luật*

---

## 📡 6. Cách Đăng Lên Kênh YouTube Thảo Dương TV

Khi bạn đã duyệt xong video và sẵn sàng đăng:
1. Bạn có thể sử dụng công cụ upload terminal có sẵn:
   ```bash
   python3 ../1995lido_youtube_management/yt_upload.py static/output/motivation_short_01.mp4 --title "Quy Tắc 2 Phút Thay Đổi Cả Ngày Của Bạn #Shorts" --privacy public
   ```
2. Hoặc tải trực tiếp file `motivation_short_XX.mp4` lên ứng dụng YouTube / YouTube Studio từ điện thoại và sao chép tiêu đề, mô tả đã soạn sẵn trong `data/motivation_20_shorts.json`.
