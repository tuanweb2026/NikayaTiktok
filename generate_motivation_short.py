#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_motivation_short.py
Tạo 1 video Short thử nghiệm theo chủ đề Cảm Hứng / Năng Lượng Sống
- Tiêu đề: "Quy Tắc 2 Phút Thay Đổi Cả Ngày Của Bạn"
- Nền: thiên nhiên bình minh + overlay gradient tím-xanh đẹp
- Giọng đọc: vi-VN-HoaiMyNeural miền Nam ấm áp
- Nhạc nền: nhac_chill_zen.wav nhẹ nhàng
"""

import os
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

# ------------ CẤU HÌNH -------------------------------------------
FFMPEG_PATH = "./bin/ffmpeg"
EDGE_TTS_PATH = "/Users/abc/Library/Python/3.9/bin/edge-tts"
ASSETS_DIR = "static/assets"
OUTPUT_DIR = "static/output"
BG_MUSIC = os.path.join(ASSETS_DIR, "nhac_chill_zen.wav")
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"

SHORT_01 = {
    "id": "motivation_01",
    "title": "Quy Tắc 2 Phút Thay Đổi Cả Ngày Của Bạn",
    "hook": "Quy Tắc 2 Phút Thay Đổi Cả Ngày",
    "script": (
        "Bạn có biết chỉ cần 2 phút mỗi sáng là đủ để não bộ chuyển sang chế độ tập trung cao độ không? "
        "Khi thức dậy, thay vì cầm điện thoại, hãy dành 2 phút nhắm mắt hít thở sâu. "
        "Khoa học chứng minh điều này kích hoạt vỏ não trước trán, giúp bạn ra quyết định sáng suốt hơn suốt cả ngày. "
        "Thử ngay sáng mai bạn nhen! Đăng Ký kênh Thảo Dương TV để nhận năng lượng tích cực mỗi ngày."
    ),
    "bg": "buddha_2.jpg",  # dùng hình nền zen sẵn có
}

OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "motivation_01_preview.mp4")

# ------------ TẠO FRAME ẢNH NÂNG CẤP (Gradient header + big text) ----------

def wrap_text(text, max_chars=22):
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

def create_motivation_frame(title, hook, bg_image_name, output_img_path, width=720, height=1280):
    bg_path = os.path.join(ASSETS_DIR, bg_image_name)
    if not os.path.exists(bg_path):
        bg_path = os.path.join(ASSETS_DIR, "buddha_1.jpg")

    bg_im = Image.open(bg_path)

    # Scale & Center Crop
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

    # Dark overlay
    overlay = Image.new('RGBA', bg_frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Heavy dark gradient at top and bottom for readability
    for y in range(300):
        alpha = int(200 * (1 - y / 300))
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    for y in range(height - 350, height):
        alpha = int(220 * ((y - (height - 350)) / 350))
        draw.line([(0, y), (width, y)], fill=(10, 10, 40, alpha))

    # Soft overall vignette
    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 55))

    # --- TOP badge: "Thảo Dương TV" ---
    try:
        font_badge = ImageFont.truetype(FONT_PATH, 28)
    except IOError:
        font_badge = ImageFont.load_default()

    badge_text = "✨ THẢO DƯƠNG TV"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    bx = (width - bw) // 2
    draw.rounded_rectangle([bx - 18, 60, bx + bw + 18, 60 + 44], radius=22, fill=(255, 193, 7, 200))
    draw.text((bx, 64), badge_text, font=font_badge, fill=(0, 0, 0, 255))

    # --- MAIN TITLE (center, large) ---
    try:
        font_title = ImageFont.truetype(FONT_PATH, 52)
    except IOError:
        font_title = ImageFont.load_default()

    title_lines = wrap_text(title, max_chars=18)
    line_heights = []
    for line in title_lines:
        b = draw.textbbox((0, 0), line, font=font_title)
        line_heights.append(b[3] - b[1])

    total_h = sum(line_heights) + 16 * (len(title_lines) - 1)
    box_pad = 32
    box_w = int(width * 0.88)
    box_h = total_h + box_pad * 2
    bx1 = (width - box_w) // 2
    # Position box in CENTER
    by1 = (height - box_h) // 2 - 40
    bx2 = bx1 + box_w
    by2 = by1 + box_h

    # Glossy dark card
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=20, fill=(0, 0, 0, 160))
    # Gold left border accent
    draw.rounded_rectangle([bx1, by1, bx1 + 6, by2], radius=3, fill=(245, 158, 11, 255))

    cy = by1 + box_pad
    for i, line in enumerate(title_lines):
        b = draw.textbbox((0, 0), line, font=font_title)
        lw = b[2] - b[0]
        x = (width - lw) // 2
        # Shadow
        draw.text((x + 2, cy + 2), line, font=font_title, fill=(0, 0, 0, 220))
        # Gold text
        draw.text((x, cy), line, font=font_title, fill=(255, 214, 0, 255))
        cy += line_heights[i] + 16

    # --- BOTTOM instruction text ---
    try:
        font_sub = ImageFont.truetype(FONT_PATH, 30)
    except IOError:
        font_sub = ImageFont.load_default()

    sub_text = "👇 Đăng Ký Để Nhận Năng Lượng Mỗi Ngày"
    sb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sb[2] - sb[0]
    sx = (width - sw) // 2
    draw.text((sx + 1, height - 100 + 1), sub_text, font=font_sub, fill=(0, 0, 0, 200))
    draw.text((sx, height - 100), sub_text, font=font_sub, fill=(255, 255, 255, 240))

    final = Image.alpha_composite(bg_frame.convert('RGBA'), overlay)
    final.convert('RGB').save(output_img_path, 'JPEG', quality=95)
    print(f"✅ Frame created: {output_img_path}")


def synthesize_voice(text, output_mp3, retries=3):
    cmd = [EDGE_TTS_PATH, "--voice", "vi-VN-HoaiMyNeural", "--text", text, "--write-media", output_mp3]
    for attempt in range(retries):
        try:
            if os.path.exists(output_mp3):
                os.remove(output_mp3)
            subprocess.run(cmd, check=True, capture_output=True)
            if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 500:
                return True
        except Exception as e:
            print(f"  TTS attempt {attempt + 1} failed: {e}")
            time.sleep(2 * (attempt + 1))
    return False


def get_audio_duration(wav_path):
    res = subprocess.run([FFMPEG_PATH, "-i", wav_path], stderr=subprocess.PIPE, text=True)
    for line in res.stderr.split('\n'):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 20.0


def render_motivation_video():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    item = SHORT_01

    img_path = f"static/output/tmp_mot_frame.jpg"
    voice_mp3 = f"static/output/tmp_mot_voice.mp3"
    voice_wav = f"static/output/tmp_mot_voice.wav"
    mixed_audio = f"static/output/tmp_mot_audio.wav"
    raw_video = f"static/output/tmp_mot_raw.mp4"

    print(f"\n{'='*55}")
    print(f"🎬 RENDER: {item['title']}")
    print(f"{'='*55}\n")

    # 1. Create frame image
    print("🖼️  Tạo khung hình ảnh nền...")
    create_motivation_frame(item["title"], item["hook"], item["bg"], img_path)

    # 2. Synthesize voice
    print("\n🎙️  Tổng hợp giọng đọc HoàiMy miền Nam...")
    speak_text = item["script"]
    success = synthesize_voice(speak_text, voice_mp3)
    if not success:
        print("❌ Không thể tổng hợp giọng đọc. Dừng.")
        return False

    # 3. Convert to WAV
    subprocess.run([FFMPEG_PATH, "-y", "-i", voice_mp3, voice_wav], check=True, capture_output=True)
    duration = get_audio_duration(voice_wav)
    duration = max(15.0, min(duration, 35.0))
    print(f"  Thời lượng giọng đọc: {duration:.2f}s")

    # 4. Render raw video from image
    print("\n🎞️  Dựng video từ khung hình ảnh...")
    subprocess.run([
        FFMPEG_PATH, "-y",
        "-loop", "1", "-i", img_path,
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=720:1280",
        raw_video
    ], check=True, capture_output=True)

    # 5. Mix voice + music
    print("🎵  Trộn giọng đọc với nhạc thiền zen...")
    subprocess.run([
        FFMPEG_PATH, "-y",
        "-i", voice_wav,
        "-stream_loop", "-1", "-i", BG_MUSIC,
        "-filter_complex", "[0:a]volume=1.3[a0];[1:a]volume=0.18[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
        "-map", "[aout]",
        mixed_audio
    ], check=True, capture_output=True)

    # 6. Merge video + audio
    print("📦  Ghép video và âm thanh cuối cùng...")
    subprocess.run([
        FFMPEG_PATH, "-y",
        "-i", raw_video,
        "-i", mixed_audio,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-af", f"afade=t=out:st={duration-2:.2f}:d=2",
        "-t", f"{duration:.2f}",
        OUTPUT_VIDEO
    ], check=True, capture_output=True)

    # Cleanup
    for f in [img_path, voice_mp3, voice_wav, mixed_audio, raw_video]:
        if os.path.exists(f):
            os.remove(f)

    print(f"\n{'='*55}")
    print(f"✅ VIDEO HOÀN THÀNH: {OUTPUT_VIDEO}")
    size_kb = os.path.getsize(OUTPUT_VIDEO) / 1024
    print(f"   Kích thước: {size_kb:.0f} KB | Thời lượng: {duration:.1f}s")
    print(f"   Xem tại: http://127.0.0.1:5001/static/output/motivation_01_preview.mp4")
    print(f"{'='*55}\n")
    return True


if __name__ == "__main__":
    render_motivation_video()
