from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
import json
import os
import subprocess

app = Flask(__name__)
DB_PATH = "data/database.json"
ASSETS_DIR = "static/assets"
OUTPUT_DIR = "static/output"

def load_db():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    status_filter = request.args.get('status', 'pending')
    page = int(request.args.get('page', 1))
    per_page = 50
    
    posts = load_db()
    
    # Filter posts based on status
    filtered = [p for p in posts if p.get('status', 'pending') == status_filter]
    
    # Sort posts by ID so we see early ones first
    filtered.sort(key=lambda x: x.get('id', 0))
    
    total = len(filtered)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_posts = filtered[start_idx:end_idx]
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    # Available background images
    bg_images = ['buddha_1.jpg', 'buddha_2.jpg', 'buddha_3.jpg']
    
    # Counts
    counts = {
        'pending': len([p for p in posts if p.get('status') == 'pending']),
        'approved': len([p for p in posts if p.get('status') == 'approved']),
        'rendered': len([p for p in posts if p.get('status') == 'rendered']),
        'uploaded': len([p for p in posts if p.get('status') == 'uploaded'])
    }
    
    return render_template(
        'index.html', 
        posts=paginated_posts, 
        status_filter=status_filter, 
        bg_images=bg_images, 
        counts=counts,
        page=page,
        total_pages=total_pages,
        total_count=total
    )

@app.route('/update/<int:post_id>', methods=['POST'])
def update_post(post_id):
    posts = load_db()
    post = next((p for p in posts if p['id'] == post_id), None)
    if post:
        post['title'] = request.form.get('title', post.get('title', ''))
        post['summary'] = request.form.get('summary', post.get('summary', ''))
        post['content'] = request.form.get('content', post['content'])
        post['image_bg'] = request.form.get('image_bg', post.get('image_bg', 'buddha_1.jpg'))
        post['status'] = request.form.get('status', post['status'])
        save_db(posts)
    return redirect(url_for('index', status=post['status'] if post else 'pending'))

@app.route('/render/<int:post_id>', methods=['POST'])
def render_post_video(post_id):
    try:
        # Run generator script
        result = subprocess.run(['./venv/bin/python3', 'generate_video.py', str(post_id)], capture_output=True, text=True, check=True)
        return jsonify({"success": True, "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr or str(e)}), 500

@app.route('/upload/<int:post_id>', methods=['POST'])
def upload_post_video(post_id):
    try:
        # Run uploader script
        result = subprocess.run(['./venv/bin/python3', 'upload_tiktok.py', str(post_id)], capture_output=True, text=True, check=True)
        return jsonify({"success": True, "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": e.stderr or str(e)}), 500

@app.route('/video/<int:post_id>')
def serve_video(post_id):
    return send_from_directory(OUTPUT_DIR, f"post_{post_id}.mp4")

YT_DB_PATH = "data/youtube_60_shorts.json"

def load_yt_db():
    if not os.path.exists(YT_DB_PATH):
        return []
    with open(YT_DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_yt_db(data):
    with open(YT_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/youtube')
def youtube_review():
    shorts = load_yt_db()
    return render_template('youtube_review.html', shorts=shorts)

@app.route('/update_youtube/<int:order>', methods=['POST'])
def update_youtube_short(order):
    data = request.get_json() or {}
    new_title = data.get('youtube_title', '').strip()
    new_desc = data.get('youtube_description', '').strip()

    shorts = load_yt_db()
    item = next((s for s in shorts if s.get('order') == order), None)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    if new_title:
        item['youtube_title'] = new_title
    if new_desc:
        item['youtube_description'] = new_desc

    save_yt_db(shorts)

    # Also update main database.json if matched
    pid = item.get('id')
    if pid:
        posts = load_db()
        post = next((p for p in posts if p.get('id') == pid), None)
        if post:
            if new_title:
                post['youtube_title'] = new_title
            if new_desc:
                post['youtube_description'] = new_desc
            save_db(posts)

    return jsonify({"success": True, "message": "Updated successfully"})

@app.route('/api/youtube_shorts')
def api_youtube_shorts():
    shorts = load_yt_db()
    return jsonify(shorts)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(host='127.0.0.1', port=5001, debug=True)
