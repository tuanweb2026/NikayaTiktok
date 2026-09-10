#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ytb_goldentime_daemon.py
Daemon tự động đăng 20 Shorts theo Khung Giờ Vàng (Golden Time Slots) trong 7 ngày:
  - Khung Sáng: 07:00 - 07:30 (Đăng video Năng lượng buổi sáng)
  - Khung Trưa: 11:30 - 12:30 (Đăng video Yêu đời & Gia đình)
  - Khung Tối : 19:30 - 20:30 (Đăng video Kỷ luật & Phát triển bản thân)
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

BASE_DIR = Path("/Users/abc/.gemini/antigravity/scratch/tiktok_nikaya")
YTB_MGR_DIR = Path("/Users/abc/.gemini/antigravity/scratch/1995lido_youtube_management")
SCHEDULE_FILE = BASE_DIR / "data" / "golden_schedule_20_shorts.json"
LOG_FILE = BASE_DIR / "data" / "golden_daemon.log"
PID_FILE = BASE_DIR / "data" / "golden_daemon.pid"

# Import thư viện YouTube upload
sys.path.insert(0, str(YTB_MGR_DIR))
try:
    import yt_upload
except ImportError:
    yt_upload = None

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_schedule():
    if not SCHEDULE_FILE.exists():
        log(f"Lỗi: Không tìm thấy file {SCHEDULE_FILE}")
        return None
    with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_schedule(data):
    try:
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"Lỗi khi lưu schedule: {e}")

def run_daemon():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log("="*65)
    log("KHỞI CHẠY DAEMON ĐĂNG 20 SHORTS THEO KHUNG GIỜ VÀNG (7 NGÀY)")
    log(f"  - PID: {os.getpid()}")
    log("  - Khung giờ: Sáng 07:00 | Trưa 11:45 | Tối 20:00")
    log("="*65)

    while True:
        data = load_schedule()
        if not data:
            time.sleep(60)
            continue

        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M")

        # Tìm các video đến giờ đăng nhưng trạng thái là 'pending'
        pending_items = [it for it in data["items"] if it.get("status") == "pending"]
        if not pending_items:
            log("🎉 TẤT CẢ 20 VIDEO THEO LỊCH TRÌNH ĐÃ ĐƯỢC ĐĂNG HOÀN TẤT!")
            break

        for item in pending_items:
            target_dt_str = item["scheduled_datetime"]
            target_dt = datetime.datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M")

            # Nếu thời gian hiện tại đã tới hoặc qua giờ hẹn (trong vòng 30 phút)
            diff_sec = (now - target_dt).total_seconds()
            if 0 <= diff_sec <= 1800:
                log(f">>> ĐẾN GIỜ ĐĂNG: Short #{item['id']} ({item['slot_name']}) - {item['title']}")

                # Kiểm tra token
                tokens = yt_upload.get_tokens() if yt_upload else None
                if not tokens:
                    log("Cảnh báo: Chưa lấy được YouTube token, chờ 60s...")
                    time.sleep(60)
                    break

                # Thực hiện upload
                vid_id, err = yt_upload.upload_one(
                    filepath=item["file_path"],
                    title=item["title"],
                    description=item["description"],
                    tags=item.get("tags", ["Shorts", "ThaoDuongTV"]),
                    privacy="public",
                    tokens=tokens
                )

                if vid_id:
                    item["status"] = "uploaded"
                    item["youtube_id"] = vid_id
                    item["uploaded_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_schedule(data)
                    log(f"✅ ĐĂNG THÀNH CÔNG Short #{item['id']}! Link: https://youtube.com/shorts/{vid_id}")
                else:
                    item["status"] = "error"
                    item["error_msg"] = str(err)
                    save_schedule(data)
                    log(f"❌ LỖI ĐĂNG Short #{item['id']}: {err}")

        # Kiểm tra lại mỗi 30 giây
        time.sleep(30)

if __name__ == "__main__":
    run_daemon()
