#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ytb_nikaya_daemon.py
Tự động upload 151+ video Phật Giáo Nikaya lên kênh YouTube Shorts Thảo Dương TV.
- Đăng ngược từ post_165.mp4 lùi dần về post_1.mp4.
- Tần suất: 10 phút / bài.
- Khung giờ hoạt động:
    + Buổi tối: từ bây giờ đến 23:30 (dừng/nghỉ ngơi ban đêm).
    + Buổi sáng: tự động tiếp tục từ 07:00 sáng hôm sau.
- Chạy nền độc lập dưới dạng daemon, không phụ thuộc vào IDE hay Antigravity.
- Lưu trữ lịch sử và trạng thái vào ytb_upload_queue.json và ytb_daemon.log.
"""

import os
import sys
import json
import time
import datetime
import subprocess
from pathlib import Path

BASE_DIR = Path("/Users/abc/.gemini/antigravity/scratch/tiktok_nikaya")
YTB_MGR_DIR = Path("/Users/abc/.gemini/antigravity/scratch/1995lido_youtube_management")
DB_PATH = BASE_DIR / "data" / "database.json"
QUEUE_PATH = BASE_DIR / "data" / "ytb_upload_queue.json"
LOG_FILE = BASE_DIR / "data" / "ytb_daemon.log"
PID_FILE = BASE_DIR / "data" / "ytb_daemon.pid"

# Import thư viện YouTube upload từ 1995lido_youtube_management
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
    """
    Kiểm tra thời gian hiện tại có thuộc khung giờ được phép upload không:
    - Từ 07:00 đến 23:30 mỗi ngày: TRUE
    - Từ 23:30 đến 07:00 sáng hôm sau: FALSE (nghỉ ngơi ban đêm)
    """
    if now is None:
        now = datetime.datetime.now()
    
    current_minutes = now.hour * 60 + now.minute
    start_morning = 7 * 60         # 07:00 (420 phút)
    end_night = 23 * 60 + 30       # 23:30 (1410 phút)
    
    return start_morning <= current_minutes <= end_night

def seconds_until_allowed_hours(now=None):
    """
    Tính số giây cần ngủ nếu đang ngoài khung giờ (ví dụ đang sau 23:30, chờ đến 07:00 sáng).
    """
    if now is None:
        now = datetime.datetime.now()
        
    current_minutes = now.hour * 60 + now.minute
    end_night = 23 * 60 + 30       # 23:30
    start_morning = 7 * 60         # 07:00

    if current_minutes > end_night:
        # Đã quá 23:30, cần chờ đến 07:00 sáng hôm sau
        target = (now + datetime.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
        return max(60, int((target - now).total_seconds()))
    elif current_minutes < start_morning:
        # Đang giữa 00:00 và 07:00 sáng nay
        target = now.replace(hour=7, minute=0, second=0, microsecond=0)
        return max(60, int((target - now).total_seconds()))
    else:
        return 0

def init_queue():
    """Khởi tạo danh sách hàng đợi nếu chưa có"""
    if QUEUE_PATH.exists():
        try:
            with open(QUEUE_PATH, "r", encoding="utf-8") as f:
                queue_data = json.load(f)
                return queue_data
        except Exception as e:
            log(f"Lỗi đọc queue hiện tại ({e}), sẽ tái tạo queue mới...")

    # Đọc database để lấy title và nội dung chuẩn
    posts_by_id = {}
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                for p in json.load(f):
                    posts_by_id[p["id"]] = p
        except Exception as e:
            log(f"Cảnh báo khi đọc database.json: {e}")

    items = []
    # Đăng ngược từ 165 về 1
    for pid in range(165, 0, -1):
        video_path = BASE_DIR / "static" / "output" / f"post_{pid}.mp4"
        if not video_path.exists():
            continue

        p_info = posts_by_id.get(pid, {})
        title_raw = p_info.get("title", f"Kinh Nikaya - Lời Phật Dạy #{pid}")
        summary_raw = p_info.get("summary", p_info.get("content", ""))

        # Clean title cho YouTube Shorts
        clean_title = title_raw.strip()
        if not clean_title.endswith("#Shorts"):
            clean_title = f"{clean_title} #Shorts"

        description = f"""{clean_title}

📖 Lời Phật Dạy Từ Kinh Nikaya:
"{summary_raw}"

✨ Lời nhắn nhủ từ Thảo Dương TV:
Mỗi ngày dành 20 giây lắng đọng tâm hồn, nuôi dưỡng lòng từ bi và chánh niệm giữa cuộc sống bộn bề.

🙏 Nếu thấy video ý nghĩa và đem lại an lạc, hoan hỷ nhấn ĐĂNG KÝ KÊNH YouTube Thảo Dương TV để cùng gieo duyên lành và đón nhận lời kinh Phật dạy mỗi ngày bạn nhé! Cảm ơn bạn rất nhiều.

🔔 Đăng Ký Kênh: https://www.youtube.com/@ThaoDuongTV

#Shorts #ThaoDuongTV #KinhNikaya #LoiPhatDay #PhatGiao #DaoPhat #Thien #NhacThien #AnLac #TrietLyCuocSong #ChanhNiem #PhatPhap
""".strip()

        tags = [
            "Shorts", "Thao Duong TV", "Kinh Nikaya", "Loi Phat Day", 
            "Phat Giao", "Dao Phat", "Thien", "Nhac Thien", "An Lac", 
            "Triet Ly Cuoc Song", "Chanh Niem", "Phat Phap"
        ]

        items.append({
            "id": pid,
            "file_path": str(video_path),
            "title": clean_title,
            "description": description,
            "tags": tags,
            "privacy": "public",
            "status": "pending",  # pending, uploading, uploaded, error
            "youtube_id": None,
            "uploaded_at": None,
            "error_msg": None
        })

    queue_data = {
        "created_at": datetime.datetime.now().isoformat(),
        "total_items": len(items),
        "uploaded_count": 0,
        "items": items
    }

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, ensure_ascii=False, indent=2)

    log(f"Đã khởi tạo hàng đợi gồm {len(items)} video (đăng ngược từ 165 về 1)")
    return queue_data

def save_queue(queue_data):
    try:
        with open(QUEUE_PATH, "w", encoding="utf-8") as f:
            json.dump(queue_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"Lỗi khi lưu queue_data: {e}")

def run_daemon():
    # Ghi PID
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    log("="*60)
    log("KHỞI CHẠY DAEMON UPLOAD YOUTUBE SHORTS - KÊNH THẢO DƯƠNG TV")
    log("Cấu hình:")
    log("  - Khoảng cách: 10 phút / 1 video")
    log("  - Khung giờ hoạt động: 07:00 - 23:30 hàng ngày")
    log("  - Thứ tự: Đăng ngược từ post_165.mp4 đến post_1.mp4")
    log(f"  - PID: {os.getpid()}")
    log("="*60)

    queue_data = init_queue()

    while True:
        now = datetime.datetime.now()

        # 1. Kiểm tra khung giờ hoạt động
        if not is_within_allowed_hours(now):
            sec_to_wait = seconds_until_allowed_hours(now)
            resume_time = now + datetime.timedelta(seconds=sec_to_wait)
            log(f"Đã ngoài khung giờ hoạt động (23:30 - 07:00). Daemon tạm nghỉ {sec_to_wait // 60} phút.")
            log(f"Dự kiến tiếp tục lúc: {resume_time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(min(sec_to_wait, 300))  # Thức dậy mỗi 5 phút để check lại
            continue

        # 2. Tìm bài tiếp theo cần upload
        next_item = None
        for item in queue_data.get("items", []):
            if item.get("status") == "pending":
                next_item = item
                break

        if not next_item:
            log("Tất cả các video trong hàng đợi đã được upload hoàn tất! Daemon kết thúc thành công.")
            break

        # 3. Lấy token mới nhất từ YouTube OAuth
        log(f">>> Chuẩn bị đăng: Post ID #{next_item['id']} ({next_item['title'][:50]}...)")
        tokens = None
        if yt_upload:
            tokens = yt_upload.get_tokens()

        if not tokens:
            log("Cảnh báo: Không lấy được YouTube access token! Sẽ thử lại sau 60s...")
            time.sleep(60)
            continue

        # 4. Thực hiện upload
        video_id, err_msg = yt_upload.upload_one(
            filepath=next_item["file_path"],
            title=next_item["title"],
            description=next_item["description"],
            tags=next_item["tags"],
            privacy=next_item["privacy"],
            tokens=tokens
        )

        if video_id:
            next_item["status"] = "uploaded"
            next_item["youtube_id"] = video_id
            next_item["uploaded_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            next_item["error_msg"] = None
            queue_data["uploaded_count"] = sum(1 for x in queue_data["items"] if x.get("status") == "uploaded")
            save_queue(queue_data)
            
            yt_link = f"https://youtube.com/shorts/{video_id}"
            log(f"THÀNH CÔNG: Đã đăng Post #{next_item['id']} lên YouTube Shorts!")
            log(f"Link xem: {yt_link} (Đã đăng: {queue_data['uploaded_count']}/{queue_data['total_items']})")
        else:
            next_item["status"] = "error"
            next_item["error_msg"] = str(err_msg)
            save_queue(queue_data)
            log(f"THẤT BẠI: Lỗi đăng Post #{next_item['id']}: {err_msg}")

        # 5. Chờ 10 phút trước video tiếp theo (600 giây)
        log("Đang nghỉ 10 phút (600 giây) cho bài tiếp theo theo đúng lịch trình...")
        # Chia nhỏ sleep thành các block 30s để có thể log liveness
        for step_i in range(20):
            time.sleep(30)

if __name__ == "__main__":
    run_daemon()
