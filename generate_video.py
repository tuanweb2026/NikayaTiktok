import os
import subprocess
import json
import re
from PIL import Image, ImageDraw, ImageFont

# Configurations
FFMPEG_PATH = "./bin/ffmpeg"
EDGE_TTS_PATH = "/Users/abc/Library/Python/3.9/bin/edge-tts"
ASSETS_DIR = "static/assets"
OUTPUT_DIR = "static/output"
DB_PATH = "data/database.json"

FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
FONT_SIZE_TITLE = 44
BG_MUSIC = os.path.join(ASSETS_DIR, "nhac_chill_zen.wav")

def wrap_text(text, max_chars=20):
    """Wrap text to maximum chars per line without splitting words."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        if len(" ".join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def create_image_frame(title, bg_image_name, output_img_path, width=720, height=1280):
    """Create a 720x1280 vertical frame with centered title ONLY and dark overlay."""
    # 1. Load background image
    bg_path = os.path.join(ASSETS_DIR, bg_image_name)
    if not os.path.exists(bg_path):
        bg_path = os.path.join(ASSETS_DIR, "buddha_1.jpg")
        
    bg_im = Image.open(bg_path)
    
    # 2. Scale and Center Crop background to target width x height
    bg_ratio = bg_im.width / bg_im.height
    target_ratio = width / height
    
    if bg_ratio > target_ratio:
        new_h = height
        new_w = int(bg_im.width * (height / bg_im.height))
        resized = bg_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - width) // 2
        bg_frame = resized.crop((left, 0, left + width, height))
    else:
        new_w = width
        new_h = int(bg_im.height * (width / bg_im.width))
        resized = bg_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - height) // 2
        bg_frame = resized.crop((0, top, width, top + height))
        
    # 3. Create Draw object and add a dark semi-transparent overlay
    overlay = Image.new('RGBA', bg_frame.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Soft overall vignette overlay
    draw_overlay.rectangle([0, 0, width, height], fill=(0, 0, 0, 80))
    
    # 4. Render Font
    try:
        font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
    except IOError:
        font_title = ImageFont.load_default()
        
    # Wrap title
    title_wrapped = wrap_text(title, max_chars=20)
    
    # Calculate heights for sizing card background
    title_heights = []
    for line in title_wrapped:
        bbox = draw_overlay.textbbox((0, 0), line, font=font_title)
        title_heights.append(bbox[3] - bbox[1])
        
    total_title_h = sum(title_heights) + 12 * (len(title_wrapped) - 1)
    
    # Draw a small, elegant rounded box card behind Title
    box_w = int(width * 0.85)
    box_h = total_title_h + 80
    box_x1 = (width - box_w) // 2
    box_y1 = (height - box_h) // 2
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h
    
    draw_overlay.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=15, fill=(0, 0, 0, 140))
    
    # Write Title lines (centered, Amber/Gold color)
    current_y = box_y1 + 40
    for line in title_wrapped:
        bbox = draw_overlay.textbbox((0, 0), line, font=font_title)
        line_w = bbox[2] - bbox[0]
        x = (width - line_w) // 2
        # Shadow
        draw_overlay.text((x + 2, current_y + 2), line, font=font_title, fill=(0, 0, 0, 240))
        # Title (Amber/Golden)
        draw_overlay.text((x, current_y), line, font=font_title, fill=(245, 158, 11, 255))
        current_y += bbox[3] - bbox[1] + 12
        
    # Composite the overlay onto background image
    final_frame = Image.alpha_composite(bg_frame.convert('RGBA'), overlay)
    final_frame.convert('RGB').save(output_img_path, 'JPEG', quality=95)
    print(f"Generated frame image (Title only): {output_img_path}")

def render_video_for_post(post_id):
    """Render a TikTok video displaying Title only and playing realistic Hoai My Southern Voiceover."""
    print(f"Starting video render for Post ID {post_id}")
    
    # 1. Fetch post from DB
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return False
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        print(f"Post {post_id} not found in database.")
        return False
        
    title = post.get("title", f"Lời Phật Dạy #{post_id}")
    content = post.get("summary", post["content"])
    bg_image = post.get("image_bg", "buddha_1.jpg")
    
    # Prepare paths
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img_path = f"static/output/temp_frame_{post_id}.jpg"
    voice_mp3 = f"static/output/temp_voice_{post_id}.mp3"
    voice_wav = f"static/output/temp_voice_{post_id}.wav"
    final_audio = f"static/output/temp_audio_mixed_{post_id}.wav"
    raw_video_path = f"static/output/temp_raw_{post_id}.mp4"
    final_output_path = os.path.join(OUTPUT_DIR, f"post_{post_id}.mp4")
    
    # Clean tags from speech text
    speak_text = content.replace("Thảo Dương TV", "").replace("nhen!", "").replace("nghen!", "").replace("nhe!", "").replace("nè", "").strip()
    
    # 2. Synthesize High-Fidelity Southern voice via Edge-TTS (vi-VN-HoaiMyNeural) with retries
    print("🎙️ Synthesizing Southern HoaiMyNeural Voice...")
    tts_cmd = [
        EDGE_TTS_PATH,
        "--voice", "vi-VN-HoaiMyNeural",
        "--text", speak_text,
        "--write-media", voice_mp3
    ]
    print(f"Running edge-tts command: {' '.join(tts_cmd)}")
    
    max_retries = 3
    import time
    for attempt in range(max_retries):
        try:
            if os.path.exists(voice_mp3):
                os.remove(voice_mp3)
            subprocess.run(tts_cmd, check=True)
            if os.path.exists(voice_mp3) and os.path.getsize(voice_mp3) > 100:
                break
            else:
                raise Exception("Tệp âm thanh trống hoặc không tồn tại.")
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Lỗi: Không thể tạo TTS sau {max_retries} lần thử.")
                raise e
            wait_time = 2 * (attempt + 1)
            print(f"Cảnh báo: Edge-TTS gặp lỗi: {e}. Thử lại sau {wait_time} giây...")
            time.sleep(wait_time)
    
    # Convert to WAV for mixing
    subprocess.run([FFMPEG_PATH, "-y", "-i", voice_mp3, voice_wav], check=True)
    
    # 3. Measure voice duration
    res = subprocess.run([FFMPEG_PATH, "-i", voice_wav], stderr=subprocess.PIPE, text=True)
    duration = 20.0
    for line in res.stderr.split('\n'):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            duration = float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            break
    print(f"HoaiMy base voice duration: {duration:.2f}s")
    
    if duration < 15.0:
        duration = 15.0
    elif duration > 28.0:
        duration = 28.0
        
    # 4. Create image frame with Title ONLY
    create_image_frame(title, bg_image, img_path)
    
    # 5. Render raw video matching voiceover duration
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1",
        "-i", img_path,
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=720:1280",
        raw_video_path
    ]
    print(f"Rendering raw video: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # 6. Mix voice and zen music
    print("Mixing voice and zen background music...")
    mix_cmd = [
        FFMPEG_PATH, "-y",
        "-i", voice_wav,
        "-stream_loop", "-1",
        "-i", BG_MUSIC,
        "-filter_complex", "[0:a]volume=1.4[a0];[1:a]volume=0.20[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
        "-map", "[aout]",
        final_audio
    ]
    subprocess.run(mix_cmd, check=True)
    
    # 7. Merge video and audio with final fade-out
    print("Merging video and audio...")
    merge_cmd = [
        FFMPEG_PATH, "-y",
        "-i", raw_video_path,
        "-i", final_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-af", f"afade=t=out:st={duration-2:.2f}:d=2",
        "-t", f"{duration:.2f}",
        final_output_path
    ]
    subprocess.run(merge_cmd, check=True)
    
    # Clean up temp files
    for temp_f in [img_path, voice_mp3, voice_wav, final_audio, raw_video_path]:
        if os.path.exists(temp_f):
            os.remove(temp_f)
            
    print(f"Successfully rendered video: {final_output_path}")
    
    # Update DB status
    post["status"] = "rendered"
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
        
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            pid = int(sys.argv[1])
        except ValueError:
            print("Lỗi: ID bài đăng phải là số nguyên.")
            sys.exit(1)
            
        render_video_for_post(pid)
    else:
        print("Usage: python3 generate_video.py <post_id>")
