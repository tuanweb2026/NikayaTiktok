#!/bin/bash
# Script to manage TikTok Nikaya video generation and review app

PROJECT_DIR="/Users/abc/.gemini/antigravity/scratch/tiktok_nikaya"
cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source venv/bin/activate

show_help() {
    echo "Hệ thống tự động hóa TikTok Nikaya"
    echo "================================="
    echo "Cách sử dụng:"
    echo "  ./run.sh parse        - Chạy phân tích file PDF và cập nhật cơ sở dữ liệu"
    echo "  ./run.sh web          - Khởi chạy website review (Flask) trên cổng 5001"
    echo "  ./run.sh youtube      - Khởi chạy website review chuyên biệt cho 60 YouTube Shorts"
    echo "  ./run.sh render <id>  - Tạo video (20s) bằng FFmpeg cho bài viết có ID cụ thể"
    echo "  ./run.sh upload <id>  - Tải lên tự động video có ID cụ thể lên TikTok"
    echo "  ./run.sh help         - Hiển thị hướng dẫn này"
}

case "$1" in
    parse)
        echo "Bắt đầu phân tích PDF..."
        python3 parse_pdf.py
        ;;
    web)
        echo "Khởi chạy Web Review..."
        echo "Vui lòng mở trình duyệt và truy cập: http://127.0.0.1:5001"
        python3 app.py
        ;;
    render)
        if [ -z "$2" ]; then
            echo "Lỗi: Vui lòng nhập ID bài đăng (ví dụ: ./run.sh render 13)"
            exit 1
        fi
        echo "Đang tạo video cho ID $2..."
        python3 generate_video.py "$2"
        ;;
    upload)
        if [ -z "$2" ]; then
            echo "Lỗi: Vui lòng nhập ID bài đăng (ví dụ: ./run.sh upload 13)"
            exit 1
        fi
        echo "Đang tự động tải lên TikTok video ID $2..."
        python3 upload_tiktok.py "$2"
        ;;
    youtube)
        echo "Khởi chạy Web Review 60 YouTube Shorts..."
        echo "Vui lòng mở trình duyệt và truy cập: http://127.0.0.1:5001/youtube"
        python3 app.py
        ;;
    *)
        show_help
        ;;
esac
