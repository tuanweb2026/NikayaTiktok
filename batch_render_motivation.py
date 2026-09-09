#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_render_motivation.py
Script render hàng loạt hoặc đơn lẻ 20 video Shorts truyền cảm hứng / phát triển bản thân.

Cách dùng:
    # Render 1 video để test thử (ví dụ bài 1):
    python3 batch_render_motivation.py 1

    # Render tất cả 20 video:
    python3 batch_render_motivation.py all

    # Render dải ID cụ thể (ví dụ từ 1 đến 5):
    python3 batch_render_motivation.py 1 5
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).parent.resolve()
JSON_PATH = BASE_DIR / "data" / "motivation_20_shorts.json"
ASSETS_DIR = BASE_DIR / "static" / "assets"
OUTPUT_DIR = BASE_DIR / "static" / "output"
FFMPEG_PATH = Path("/usr/local/bin/ffmpeg")
if not FFMPEG_PATH.exists():
    FFMPEG_PATH = BASE_DIR / "bin" / "ffmpeg"
EDGE_TTS_PATH = "/Users/abc/Library/Python/3.9/bin/edge-tts"
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
BG_MUSIC = ASSETS_DIR / "nhac_chill_zen.wav"

def wrap_text(text, max_chars=18):
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

def create_card_frame(title_clean, bg_name, output_jpg, width=720, height=1280):
    bg_path = ASSETS_DIR / bg_name
    if not bg_path.exists():
        bg_path = ASSETS_DIR / "buddha_1.jpg"

    bg_im = Image.open(bg_path)
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

    overlay = Image.new('RGBA', bg_frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Vignette & Gradient
    for y in range(250):
        alpha = int(190 * (1 - y / 250))
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
    for y in range(height - 280, height):
        alpha = int(210 * ((y - (height - 280)) / 280))
        draw.line([(0, y), (width, y)], fill=(10, 10, 30, alpha))
    draw.rectangle([0, 0, width, height], fill=(0, 0, 0, 60))

    # Top badge
    try:
        font_badge = ImageFont.truetype(FONT_PATH, 26)
    except IOError:
        font_badge = ImageFont.load_default()

    badge_text = "✨ THẢO DƯƠNG TV"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    bx = (width - bw) // 2
    draw.rounded_rectangle([bx - 16, 50, bx + bw + 16, 50 + 40], radius=20, fill=(245, 158, 11, 220))
    draw.text((bx, 54), badge_text, font=font_badge, fill=(0, 0, 0, 255))

    # Title Card
    try:
        font_title = ImageFont.truetype(FONT_PATH, 48)
    except IOError:
        font_title = ImageFont.load_default()

    lines = wrap_text(title_clean, max_chars=18)
    line_h = []
    for l in lines:
        b = draw.textbbox((0, 0), l, font=font_title)
        line_h.append(b[3] - b[1])

    total_h = sum(line_h) + 16 * (len(lines) - 1)
    pad = 32
    box_w = int(width * 0.88)
    box_h = total_h + pad * 2
    x1 = (width - box_w) // 2
    y1 = (height - box_h) // 2 - 30
    x2 = x1 + box_w
    y2 = y1 + box_h

    draw.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=(0, 0, 0, 160))
    draw.rounded_rectangle([x1, y1, x1 + 6, y2], radius=3, fill=(245, 158, 11, 255))

    cy = y1 + pad
    for i, l in enumerate(lines):
        b = draw.textbbox((0, 0), l, font=font_title)
        lw = b[2] - b[0]
        x = (width - lw) // 2
        draw.text((x + 2, cy + 2), l, font=font_title, fill=(0, 0, 0, 230))
        draw.text((x, cy), l, font=font_title, fill=(255, 214, 0, 255))
        cy += line_h[i] + 16

    # Bottom CTA
    try:
        font_sub = ImageFont.truetype(FONT_PATH, 28)
    except IOError:
        font_sub = ImageFont.load_default()

    sub_text = "👇 Đăng Ký Để Nhận Năng Lượng Tích Cực"
    sb = draw.textbbox((0, 0), sub_text, font=font_sub)
    sw = sb[2] - sb[0]
    sx = (width - sw) // 2
    draw.text((sx + 1, height - 90 + 1), sub_text, font=font_sub, fill=(0, 0, 0, 220))
    draw.text((sx, height - 90), sub_text, font=font_sub, fill=(255, 255, 255, 240))

    final = Image.alpha_composite(bg_frame.convert('RGBA'), overlay)
    final.convert('RGB').save(output_jpg, 'JPEG', quality=95)

def synthesize_tts(text, output_mp3):
    cmd = [EDGE_TTS_PATH, "--voice", "vi-VN-HoaiMyNeural", "--text", text, "--write-media", output_mp3]
    for attempt in range(3):
        try:
            if os.path.exists(output_mp3):
                os.remove(output_mp3)
            subprocess.run(cmd, check=True, capture_output=True)
            if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 300:
                return True
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return False

def get_audio_len(wav_path):
    res = subprocess.run([str(FFMPEG_PATH), "-i", wav_path], stderr=subprocess.PIPE, text=True)
    for line in res.stderr.split('\n'):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 18.0

def render_one_short(item):
    sid = item["id"]
    title = item["title"].replace("#Shorts", "").strip()
    script = item["script"]
    bg = item.get("bg", "buddha_1.jpg")

    print(f"\n▶ Đang dựng Short #{sid}: {title}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    img_f = OUTPUT_DIR / f"tmp_m_{sid}_frame.jpg"
    voice_mp3 = OUTPUT_DIR / f"tmp_m_{sid}.mp3"
    voice_wav = OUTPUT_DIR / f"tmp_m_{sid}.wav"
    audio_mix = OUTPUT_DIR / f"tmp_m_{sid}_mix.wav"
    raw_vid = OUTPUT_DIR / f"tmp_m_{sid}_raw.mp4"
    final_mp4 = OUTPUT_DIR / f"motivation_short_{sid:02d}.mp4"

    # 1. Tạo frame
    create_card_frame(title, bg, str(img_f))

    # 2. TTS
    ok = synthesize_tts(script, str(voice_mp3))
    if not ok:
        print(f"❌ Lỗi TTS bài {sid}")
        return False

    # 3. Convert sang WAV & tính duration
    subprocess.run([str(FFMPEG_PATH), "-y", "-i", str(voice_mp3), str(voice_wav)], check=True, capture_output=True)
    dur = get_audio_len(str(voice_wav))
    dur = max(13.0, min(dur, 28.0))

    # 4. Render video frame
    subprocess.run([
        str(FFMPEG_PATH), "-y", "-loop", "1", "-i", str(img_f),
        "-t", f"{dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", "scale=720:1280", str(raw_vid)
    ], check=True, capture_output=True)

    # 5. Mix nhạc nền zen
    subprocess.run([
        str(FFMPEG_PATH), "-y", "-i", str(voice_wav),
        "-stream_loop", "-1", "-i", str(BG_MUSIC),
        "-filter_complex", "[0:a]volume=1.35[a0];[1:a]volume=0.18[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
        "-map", "[aout]", str(audio_mix)
    ], check=True, capture_output=True)

    # 6. Ghép file MP4 cuối cùng
    subprocess.run([
        str(FFMPEG_PATH), "-y", "-i", str(raw_vid), "-i", str(audio_mix),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-af", f"afade=t=out:st={dur-2:.2f}:d=2",
        "-t", f"{dur:.2f}", str(final_mp4)
    ], check=True, capture_output=True)

    # Dọn file tạm
    for f in [img_f, voice_mp3, voice_wav, audio_mix, raw_vid]:
        if f.exists():
            f.unlink()

    sz_kb = final_mp4.stat().st_size / 1024
    print(f"✅ Hoàn thành: {final_mp4.name} ({dur:.1f}s, {sz_kb:.0f} KB)")
    return True

def main():
    if not JSON_PATH.exists():
        print(f"Không tìm thấy file: {JSON_PATH}")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        items = json.load(f)

    if len(sys.argv) == 1:
        print(__doc__)
        return

    arg1 = sys.argv[1]
    if arg1 == "all":
        print(f"=== BẮT ĐẦU RENDER TRỌN BỘ 20 VIDEO MOTIVATION SHORTS ===")
        for it in items:
            render_one_short(it)
            time.sleep(1.5)
        print("🎉 ĐÃ XONG TẤT CẢ 20 VIDEO!")
    elif len(sys.argv) == 3:
        start_id = int(sys.argv[1])
        end_id = int(sys.argv[2])
        selected = [it for it in items if start_id <= it["id"] <= end_id]
        print(f"=== RENDER TỪ BÀI #{start_id} ĐẾN #{end_id} ({len(selected)} video) ===")
        for it in selected:
            render_one_short(it)
            time.sleep(1.5)
    else:
        target_id = int(arg1)
        it = next((x for x in items if x["id"] == target_id), None)
        if not it:
            print(f"Không tìm thấy bài ID #{target_id}")
            return
        render_one_short(it)

if __name__ == "__main__":
    main()
