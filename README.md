# Hệ Thống Tự Động Hóa Video Ngắn Phật Giáo Nikaya (TikTok Nikaya Video Bot)

Dự án tự động hóa trích xuất các bài kinh Phật Giáo từ file PDF Kinh Nikaya, chuyển đổi thành kịch bản video ngắn (20 giây) truyền cảm hứng với giọng đọc thực tế Hoài Mỹ (Edge-TTS) miền Nam, ghép nhạc zen tĩnh lặng, và hỗ trợ công cụ tải lên tự động (auto-uploader) trực tiếp lên kênh TikTok thông qua giao diện Web Review trực quan hoặc Terminal.

---

## 🛠️ Tính Năng Nổi Bật

1. **Trình Phân Tích PDF (`parse_pdf.py`):** Tự động đọc và tách 1.836 bài viết từ file PDF nguồn vào cơ sở dữ liệu JSON.
2. **Biên Tập Script Tự Động (`process_all_scripts.py`):** Tự động tạo tiêu đề gợi mở và viết lại kịch bản nói theo văn phong Southern gần gũi, ấm áp của Thảo Dương TV.
3. **Bộ Dựng Video Tự Động (`generate_video.py`):**
   - Tạo video dọc chuẩn TikTok (`720x1280`).
   - Sử dụng giọng đọc AI Hoài Mỹ miền Nam truyền cảm.
   - Ghép nhạc zen thiền nền tĩnh lặng.
   - Tự động đồng bộ hóa độ dài video theo độ dài giọng đọc (tối ưu khoảng 15-20s).
   - Chỉ hiển thị Tiêu đề chữ vàng Amber trên nền tối để thu hút người xem, không đè chữ dài dòng lên hình Phật.
4. **Hệ Thống Đăng Tự Động (`upload_tiktok.py`):** Sử dụng Playwright Chromium để tự động đăng nhập bằng cookie, điền caption/hashtags, vượt qua các màn hình hướng dẫn và nhấn Đăng lên TikTok.
5. **Giao Diện Web Review (`app.py`):** Giao diện Flask nội bộ giúp xem trước, chỉnh sửa tiêu đề/kịch bản thoại, render thử video và click đăng ngay trên trình duyệt.

---

## 📂 Cấu Trúc Thư Mục Chính

```text
├── app.py                      # Backend Flask điều phối Web Review
├── generate_video.py           # Logic render video bằng FFmpeg + Pillow + Edge-TTS
├── upload_tiktok.py            # Tự động hóa đăng tải lên TikTok bằng Playwright
├── process_all_scripts.py      # Xử lý hàng loạt tiêu đề và kịch bản cho 1.825 bài đăng
├── parse_pdf.py                # Trích lọc nội dung thô từ file PDF gốc
├── run.sh                      # Script quản trị hệ thống bằng phím tắt Terminal
├── bin/
│   └── ffmpeg                  # File thực thi FFmpeg cho macOS
├── data/
│   ├── database.json           # Cơ sở dữ liệu chứa 1.836 bài viết
│   └── tiktok_cookies.json     # Cookie đăng nhập TikTok (được bảo mật trong gitignore)
├── static/
│   ├── assets/                 # Chứa ảnh nền Phật Giáo và nhạc thiền zen gốc
│   └── output/                 # Thư mục chứa các tệp video .mp4 thành phẩm (không upload lên git)
└── templates/
    └── index.html              # Giao diện Web Review phân trang mượt mà
```

---

## 🚀 Hướng Dẫn Cài Đặt

### 1. Yêu Cầu Hệ Thống
* Hệ điều hành: macOS.
* Python 3.9 trở lên.

### 2. Cài Đặt Dự Án
Di chuyển vào thư mục dự án và khởi tạo môi trường ảo Python:
```bash
git clone https://github.com/tuanweb2026/NikayaTiktok.git
cd NikayaTiktok
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 3. Cài Đặt Edge-TTS
Đảm bảo máy bạn đã cài đặt thư viện `edge-tts` (hệ thống sẽ tự gọi lệnh từ đường dẫn thư viện người dùng):
```bash
pip install edge-tts
```

---

## 🔑 Cấu Hình Đăng Nhập TikTok

Xuất file cookies từ trình duyệt của bạn (sử dụng Extension như *Get Token Cookie* hoặc *EditThisCookie* dạng JSON) khi đã đăng nhập tài khoản TikTok `@tuanweb2015`.
Lưu tệp này vào đường dẫn: **`data/tiktok_cookies.json`**.

---

## 💻 Hướng Dẫn Sử Dụng Bằng Terminal

Để chạy các lệnh tiện ích nhanh chóng, hãy sử dụng script quản trị `./run.sh`:

### 1. Khởi chạy Web Review
```bash
./run.sh web
```
Sau đó mở trình duyệt và truy cập: **[http://127.0.0.1:5001](http://127.0.0.1:5001)** để bắt đầu duyệt, sửa kịch bản và đăng bài bằng giao diện.

### 2. Dựng Video bằng Terminal
* **Tạo video đơn lẻ (ví dụ bài ID #35):**
  ```bash
  ./run.sh render 35
  ```
* **Tạo video hàng loạt (ví dụ từ bài 31 đến 45, nghỉ 1.5 giây để tránh quá tải API giọng đọc):**
  ```bash
  for i in {31..45}; do ./run.sh render $i; sleep 1.5; done
  ```

### 3. Đăng lên TikTok bằng Terminal
* **Đăng video đơn lẻ (bài ID #35):**
  ```bash
  ./run.sh upload 35
  ```
* **Đăng video hàng loạt (ví dụ từ bài 31 đến 35, nghỉ 45 giây giữa mỗi video để tránh bị TikTok quét spam):**
  ```bash
  for i in {31..35}; do ./run.sh upload $i; echo "Nghỉ 45s..."; sleep 45; done
  ```

---

## ⚠️ Lưu Ý Quan Trọng
1. **Thời gian duyệt video:** Đối với các tài khoản mới, video khi đăng lên sẽ ở chế độ riêng tư (`Only me`) và hiển thị trạng thái `⚠️ Content under review` từ 10-30 phút để kiểm duyệt tự động trước khi công khai. Đây là cơ chế mặc định của TikTok.
2. **Tránh spam:** Luôn chèn khoảng nghỉ (`sleep 45`) khi đăng hàng loạt để giữ kênh an toàn và đạt lượng tương tác tốt nhất.
