# 📘 Hướng Dẫn Quy Trình Tự Động Hóa Video Ngắn (YouTube Shorts & TikTok)
### Kênh Thảo Dương TV (@tuanweb2015) · Dự Án Kinh Nikaya

Tài liệu này hướng dẫn chi tiết từ A–Z quy trình sản xuất video ngắn Phật giáo Nikaya: từ phân tích tài liệu, biên soạn kịch bản truyền cảm hứng, kết xuất video bằng Terminal, đến tự động hóa đăng tải lên YouTube Shorts và TikTok theo lịch trình.

---

## 📑 Mục Lục
1. [Cấu Trúc Hệ Thống](#1-cấu-trúc-hệ-thống)
2. [Quy Trình 1: Phân Tích Tài Liệu & Soạn Kịch Bản](#2-quy-trình-1-phân-tích-tài-liệu--soạn-kịch-bản)
3. [Quy Trình 2: Tạo Video Ngắn Bằng Terminal](#3-quy-trình-2-tạo-video-ngắn-bằng-terminal)
4. [Quy Trình 3: Duyệt Video Trên Web Review](#4-quy-trình-3-duyệt-video-trên-web-review)
5. [Quy Trình 4: Tự Động Upload Lên YouTube Shorts (Daemon Chạy Ngầm)](#5-quy-trình-4-tự-động-upload-lên-youtube-shorts-daemon-chạy-ngầm)
6. [Quy Trình 5: Tự Động Upload Lên TikTok](#6-quy-trình-5-tự-động-upload-lên-tiktok)
7. [Bảng Lệnh Terminal Nhanh (Cheat Sheet)](#7-bảng-lệnh-terminal-nhanh-cheat-sheet)

---

## 1. Cấu Trúc Hệ Thống

```text
tiktok_nikaya/
├── run.sh                          # Phím tắt điều hành toàn bộ hệ thống
├── app.py                          # Web Review nội bộ (Cổng 5001)
├── generate_video.py               # Render video 9:16 (FFmpeg + Edge-TTS Hoài Mỹ + Nhạc Zen)
├── ytb_nikaya_daemon.py            # Daemon tự động đăng YouTube Shorts theo lịch trình
├── upload_tiktok.py                # Bot tự động đăng TikTok bằng Playwright
├── process_all_scripts.py          # Soạn kịch bản chuẩn phong cách Thảo Dương TV
├── parse_pdf.py                    # Trích xuất dữ liệu từ PDF nguồn vào database
├── data/
│   ├── database.json               # Cơ sở dữ liệu chính (1.836 bài viết)
│   ├── ytb_upload_queue.json       # Hàng đợi đăng YouTube Shorts
│   ├── ytb_daemon.log              # Nhật ký hoạt động upload YouTube
│   └── tiktok_cookies.json         # Cookie đăng nhập TikTok bảo mật
├── static/
│   ├── assets/                     # Ảnh Phật (buddha_1/2/3.jpg) và nhạc thiền (nhac_chill_zen.wav)
│   └── output/                     # Thư mục lưu trữ video thành phẩm (post_<id>.mp4)
└── templates/
    ├── index.html                  # Giao diện duyệt TikTok
    └── youtube_review.html         # Giao diện duyệt 60+ YouTube Shorts
```

---

## 2. Quy Trình 1: Phân Tích Tài Liệu & Soạn Kịch Bản

### Bước 2.1: Phân tích file PDF nguồn
Khi có tài liệu Kinh Nikaya mới ở dạng PDF, đặt file vào thư mục và chạy:
```bash
./run.sh parse
```
Hệ thống sẽ bóc tách từng bài giảng và lưu trữ vào `data/database.json`.

### Bước 2.2: Tự động biên soạn kịch bản thoại (20 giây)
Để chuyển thể các bài kinh dài thành kịch bản video ngắn gần gũi, ấm áp của miền Nam:
```bash
python3 process_all_scripts.py
```
* **Cấu trúc kịch bản tối ưu (Hook - Lời Phật Dạy - Call To Action):**
  - **Mở đầu (Hook):** Đặt vấn đề bình an gia đình hoặc câu hỏi gợi mở tâm trí.
  - **Thân bài (Body):** Trích dẫn 1 lời kinh cốt lõi (SANTUTTHI - Biết đủ, ANICCA - Vô thường, KHANTI - Nhẫn nại...).
  - **Kết thúc (CTA):** Kêu gọi đăng ký kênh Thảo Dương TV một cách chân thành, gieo duyên lành.

---

## 3. Quy Trình 2: Tạo Video Ngắn Bằng Terminal

Hệ thống sử dụng giọng đọc AI Hoài Mỹ miền Nam (`vi-VN-HoaiMyNeural`), nền nhạc thiền `nhac_chill_zen.wav` ở âm lượng 20% và hình nền tượng Phật thiêng liêng.

### 3.1. Tạo 1 video đơn lẻ (Ví dụ ID #165):
```bash
./run.sh render 165
```

### 3.2. Tạo video hàng loạt (Ví dụ từ ID 165 lùi về 140):
```bash
for i in {165..140}; do ./run.sh render $i; sleep 1.5; done
```
> **Lưu ý:** Lệnh `sleep 1.5` rất quan trọng để tránh bị Microsoft Edge-TTS giới hạn tần suất (Rate Limiting).

---

## 4. Quy Trình 3: Duyệt Video Trên Web Review

Khởi chạy máy chủ giao diện web nội bộ:
```bash
./run.sh web
```
Sau đó mở trình duyệt:
* **Giao diện YouTube Shorts:** [http://127.0.0.1:5001/youtube](http://127.0.0.1:5001/youtube)
  - Xem video phát trực tiếp trong trình duyệt.
  - Xem và chỉnh sửa trực tiếp tiêu đề, mô tả, hashtags.
  - Nút sao chép 1-click tiêu đề và mô tả.
* **Giao diện TikTok:** [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 5. Quy Trình 4: Tự Động Upload Lên YouTube Shorts (Daemon Chạy Ngầm)

Kịch bản `ytb_nikaya_daemon.py` quản trị toàn bộ việc đăng tải tự động lên YouTube Shorts theo đúng chiến lược kênh:
- **Thứ tự đăng:** Đăng ngược từ các video mới nhất `post_165.mp4` lùi dần về `post_1.mp4`.
- **Tần suất:** **10 phút / 1 video** (vừa đủ giãn cách để YouTube lập chỉ mục và phân phối view tốt).
- **Khung giờ đăng an toàn:**
  - Hoạt động từ **07:00 sáng đến 23:30 tối**.
  - Tự động tạm nghỉ lúc **23:30 đêm** và tự động tiếp tục vào **07:00 sáng hôm sau**.

### 5.1. Bật Daemon chạy ngầm độc lập (Kể cả khi tắt máy ảo/Antigravity):
```bash
nohup python3 ytb_nikaya_daemon.py >/dev/null 2>&1 &
```

### 5.2. Kiểm tra trạng thái và tiến độ upload:
```bash
# Xem 20 dòng log mới nhất
tail -n 20 data/ytb_daemon.log

# Theo dõi trực tiếp quá trình đăng (nhấn Ctrl+C để thoát theo dõi)
tail -f data/ytb_daemon.log
```

### 5.3. Dừng Daemon khi cần:
```bash
# Tìm mã PID và tắt
kill $(cat data/ytb_daemon.pid)
```

---

## 6. Quy Trình 5: Tự Động Upload Lên TikTok

Hệ thống sử dụng Playwright tự động hóa thao tác trình duyệt và đăng video qua cookie:

### 6.1. Đăng 1 video lên TikTok (Ví dụ ID #165):
```bash
./run.sh upload 165
```

### 6.2. Đăng hàng loạt lên TikTok (Nghỉ 45 giây chống spam):
```bash
for i in {165..150}; do ./run.sh upload $i; echo "Nghỉ 45s..."; sleep 45; done
```

---

## 7. Bảng Lệnh Terminal Nhanh (Cheat Sheet)

| Mục tiêu | Lệnh Terminal |
| :--- | :--- |
| **Mở Web Review** | `./run.sh web` (Truy cập `http://127.0.0.1:5001/youtube`) |
| **Render 1 video** | `./run.sh render <ID>` |
| **Render hàng loạt** | `for i in {10..20}; do ./run.sh render $i; sleep 1.5; done` |
| **Bật Daemon YouTube** | `nohup python3 ytb_nikaya_daemon.py >/dev/null 2>&1 &` |
| **Xem log upload YouTube**| `tail -f data/ytb_daemon.log` |
| **Đăng 1 video TikTok** | `./run.sh upload <ID>` |
| **Đăng hàng loạt TikTok** | `for i in {1..5}; do ./run.sh upload $i; sleep 45; done` |
