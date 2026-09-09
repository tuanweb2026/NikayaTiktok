#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ytb_motivation_daemon.py
Tự động đăng 20 video Shorts truyền cảm hứng / năng lượng tích cực lên kênh Thảo Dương TV (@tuanweb2015).
- Nguồn: data/motivation_20_shorts.json & static/output/motivation_short_XX.mp4
- Khoảng cách: 20 phút / 1 video
- Khung giờ hoạt động: 07:00 - 23:30 mỗi ngày
- Chạy nền độc lập (daemon)
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path

BASE_DIR = Path("/Users/abc/.gemini/antigravity/scratch/tiktok_nikaya")
YTB_MGR_DIR = Path("/Users/abc/.gemini/antigravity/scratch/1995lido_youtube_management")
JSON_PATH = BASE_DIR / "data" / "motivation_20_shorts.json"
QUEUE_PATH = BASE_DIR / "data" / "motivation_upload_queue.json"
LOG_FILE = BASE_DIR / "data" / "motivation_daemon.log"
PID_FILE = BASE_DIR / "data" / "motivation_daemon.pid"

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

def is_within_allowed_hours(now=None):
    if now is None:
        now = datetime.datetime.now()
    cur_m = now.hour * 60 + now.minute
    return (7 * 60) <= cur_m <= (23 * 60 + 30)

def seconds_until_morning(now=None):
    if now is None:
        now = datetime.datetime.now()
    cur_m = now.hour * 60 + now.minute
    if cur_m > (23 * 60 + 30):
        target = (now + datetime.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        return max(60, int((target - now).total_seconds()))
    elif cur_m < (7 * 60):
        target = now.replace(hour=7, minute=0, second=0, microsecond=0)
        return max(60, int((target - now).total_seconds()))
    return 0

def init_queue():
    if QUEUE_PATH.exists():
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Lỗi đọc queue ({e}), khởi tạo lại...")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    queue_items = []
    for it in items:
        sid = it["id"]
        mp4_path = BASE_DIR / "static" / "output" / f"motivation_short_{sid:02d}.mp4"
        queue_items.append({
            "id": sid,
            "title": it["title"],
            "description": it["description"],
            "tags": it.get("tags", ["Shorts", "ThaoDuongTV", "PhatTrienBanThan"]),
            "file_path": str(mp4_path),
            "privacy": "public",
            "status": "pending",
            "youtube_id": None,
            "uploaded_at": None,
            "error_msg": None
        })

    data = {
        "created_at": datetime.datetime.now().isoformat(),
        "total_items": len(queue_items),
        "uploaded_count": 0,
        "items": queue_items
    }
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def save_queue(data):
    try:
        data["uploaded_count"] = sum(1 for x in data["items"] if x.get("status") == "uploaded")
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"Lỗi lưu queue: {e}")

def run_daemon():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log("="*65)
    log("KHỞI CHẠY DAEMON UPLOAD 20 SHORTS MOTIVATION - KÊNH THẢO DƯƠNG TV")
    log(f"  - PID: {os.getpid()}")
    log("  - Giãn cách: 20 phút / 1 video")
    log("  - Khung giờ: 07:00 - 23:30 hàng ngày")
    log("="*65)

    queue = init_queue()

    while True:
        now = datetime.datetime.now()

        # Check khung giờ
        if not is_within_allowed_hours(now):
            wait_sec = seconds_until_morning(now)
            resume_dt = now + datetime.timedelta(seconds=wait_sec)
            log(f"Đêm muộn (ngoài 23:30). Daemon nghỉ đến 07:00 sáng mai ({resume_dt.strftime('%H:%M:%S')}).")
            time.sleep(min(wait_sec, 300))
            continue

        # Tìm bài tiếp theo
        next_item = None
        for it in queue["items"]:
            if it.get("status") == "pending":
                next_item = it
                break

        if not next_item:
            log("🎉 ĐÃ HOÀN TẤT UPLOAD TOÀN BỘ 20 VIDEO MOTIVATION SHORTS!")
            break

        # Chờ file MP4 sẵn sàng (nếu tiến trình render đang chạy)
        mp4_file = Path(next_item["file_path"])
        if not mp4_file.exists() or mp4_file.stat().st_size < 1024 * 100:
            log(f"File {mp4_file.name} chưa render xong, chờ 15s...")
            time.sleep(15)
            continue

        # Token check
        tokens = None
        if yt_upload:
            tokens = yt_upload.get_tokens()
        if not tokens:
            log("Lỗi: Không lấy được YouTube OAuth Token, thử lại sau 60s...")
            time.sleep(60)
            continue

        log(f">>> Đang đăng Short #{next_item['id']}: {next_item['title']}")
        vid_id, err = yt_upload.upload_one(
            filepath=next_item["file_path"],
            title=next_item["title"],
            description=next_item["description"],
            tags=next_item["tags"],
            privacy=next_item["privacy"],
            tokens=tokens
        )

        if vid_id:
            next_item["status"] = "uploaded"
            next_item["youtube_id"] = vid_id
            next_item["uploaded_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_queue(queue)
            log(f"✅ THÀNH CÔNG: Đã đăng Short #{next_item['id']}! Link: https://youtube.com/shorts/{vid_id}")
            log(f"   Tiến độ: {queue['uploaded_count']}/{queue['total_items']}")
        else:
            next_item["status"] = "error"
            next_item["error_msg"] = str(err)
            save_queue(queue)
            log(f"❌ THẤT BẠI: Short #{next_item['id']} - {err}")

        # Nghỉ 20 phút (1200s) giữa các video
        log("Đang nghỉ 20 phút (1200 giây) trước bài tiếp theo...")
        for _ in range(40):
            time.sleep(30)

if __name__ == "__main__":
    run_daemon()
