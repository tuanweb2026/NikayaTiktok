import os
import json
import re

DB_PATH = "data/database.json"
YT_DB_PATH = "data/youtube_60_shorts.json"

def clean_title_for_youtube(title):
    # Ensure title starts with clear topic and ends with #Shorts
    title = title.strip()
    # Remove existing #Shorts or #NikayaKinh if present to avoid duplication
    title = re.sub(r'#\w+', '', title).strip()
    title = re.sub(r'\s+', ' ', title)
    
    # YouTube titles are best under 90 chars + #Shorts
    if len(title) > 85:
        title = title[:82] + "..."
        
    return f"{title} #Shorts"

def build_youtube_description(title, summary, post_id):
    # Clean summary
    clean_summary = summary.strip()
    
    desc = f"""{title}

📖 Lời Phật Dạy Từ Kinh Nikaya:
"{clean_summary}"

✨ Lời nhắn nhủ từ Thảo Dương TV:
Mỗi ngày dành 20 giây lắng đọng tâm hồn, nuôi dưỡng lòng từ bi và chánh niệm giữa cuộc sống bộn bề.

🙏 Nếu thấy video ý nghĩa và đem lại an lạc, hoan hỷ nhấn ĐĂNG KÝ KÊNH YouTube Thảo Dương TV để cùng gieo duyên lành và đón nhận lời kinh Phật dạy mỗi ngày bạn nhé! Cảm ơn bạn rất nhiều.

🔔 Đăng Ký Kênh: https://www.youtube.com/@ThaoDuongTV

#Shorts #ThaoDuongTV #KinhNikaya #LoiPhatDay #PhatGiao #DaoPhat #Thien #NhacThien #AnLac #TrietLyCuocSong #ChanhNiem #PhatPhap
"""
    return desc.strip()

def prepare_youtube_60():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    # Get the 60 posts that were marked as uploaded on TikTok
    uploaded_posts = [p for p in posts if p.get('status') == 'uploaded']
    uploaded_posts.sort(key=lambda x: x.get('id', 0))
    
    if len(uploaded_posts) > 60:
        uploaded_posts = uploaded_posts[:60]
        
    print(f"Found {len(uploaded_posts)} posts to convert for YouTube Shorts.")
    
    youtube_shorts = []
    
    for idx, post in enumerate(uploaded_posts, start=1):
        pid = post['id']
        raw_title = post.get('title', f'Kinh Nikaya - Bài #{pid}')
        summary = post.get('summary', post.get('content', ''))
        
        yt_title = clean_title_for_youtube(raw_title)
        yt_desc = build_youtube_description(raw_title, summary, pid)
        yt_tags = [
            "Shorts", "Thao Duong TV", "Kinh Nikaya", "Loi Phat Day", 
            "Phat Giao", "Dao Phat", "Thien", "Nhac Thien", "An Lac", 
            "Triet Ly Cuoc Song", "Chanh Niem", "Phat Phap"
        ]
        
        video_rel_path = f"static/output/post_{pid}.mp4"
        video_exists = os.path.exists(video_rel_path)
        
        item = {
            "order": idx,
            "id": pid,
            "youtube_title": yt_title,
            "youtube_description": yt_desc,
            "youtube_tags": yt_tags,
            "video_file": video_rel_path,
            "video_exists": video_exists,
            "video_url": f"/video/{pid}",
            "original_title": raw_title,
            "summary": summary,
            "status": "ready_for_review"
        }
        
        youtube_shorts.append(item)
        
        # Also store these fields in the main database
        post['youtube_title'] = yt_title
        post['youtube_description'] = yt_desc
        post['youtube_tags'] = yt_tags
        post['youtube_status'] = "ready_for_review"
        
    # Save youtube_60_shorts.json
    with open(YT_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(youtube_shorts, f, ensure_ascii=False, indent=2)
        
    # Update database.json
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully generated {len(youtube_shorts)} YouTube Shorts in {YT_DB_PATH}")
    print(f"Verified all video files: {sum(1 for x in youtube_shorts if x['video_exists'])}/{len(youtube_shorts)} exist.")

if __name__ == "__main__":
    prepare_youtube_60()
