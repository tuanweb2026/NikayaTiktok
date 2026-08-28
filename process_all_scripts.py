import json
import os
import re

DB_PATH = "data/database.json"

def clean_text_for_speech(text):
    # Remove weird characters and keep clean text
    text = re.sub(r'[\n\r\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_core_quote(text, max_words=35):
    """Extract a concise core quote of about 30-35 words."""
    text_clean = clean_text_for_speech(text)
    # Remove bracketed titles at the start if any
    text_clean = re.sub(r'^\[[^\]]+\]\s*', '', text_clean)
    
    words = text_clean.split()
    if len(words) <= max_words:
        return " ".join(words)
        
    # Split by punctuation to end on a clean sentence
    sentences = re.split(r'(?<=[.!?])\s+', text_clean)
    current_words = []
    for s in sentences:
        s_words = s.split()
        if len(current_words) + len(s_words) <= max_words:
            current_words.extend(s_words)
        else:
            if not current_words:
                current_words.extend(s_words[:max_words])
            break
            
    res = " ".join(current_words)
    if not res.endswith(('.', '!', '?')):
        res += "..."
    return res

def generate_inspiring_title(id_num, text):
    """Generate a readable, inspiring title from the text or bracketed titles."""
    text_clean = text.strip()
    
    # Try to extract bracketed title
    bracket_match = re.match(r'^\[([^\]]+)\]', text_clean)
    if bracket_match:
        extracted = bracket_match.group(1).strip()
        # Clean title casing
        title = extracted.title()
        return f"Kinh Nikaya: {title}"
        
    # Fallback: Extract first few words as a topic
    # Remove starting punctuation/numbers
    content_clean = re.sub(r'^[0-9.\-\s]+', '', text_clean)
    content_clean = re.sub(r'^\[[^\]]+\]\s*', '', content_clean)
    words = content_clean.split()
    
    if len(words) >= 4:
        topic_words = words[:5]
        # Clean up commas, dots at end
        topic = " ".join(topic_words)
        topic = re.sub(r'[,.!?:\-]*$', '', topic).strip()
        return f"Kinh Nikaya: {topic} - Lời Khuyên Bình An"
        
    return f"Trí Tuệ Kinh Nikaya - Bài Học Ý Nghĩa #{id_num}"

def process_all_posts():
    print(f"Loading database from: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Error: database.json not found!")
        return
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    print(f"Processing {len(posts)} posts...")
    
    # Count of posts modified
    modified_count = 0
    
    for post in posts:
        pid = post["id"]
        
        # We skip the first 30 posts because they are the hand-crafted authentic ones we imported!
        if pid <= 30:
            continue
            
        original_content = post["content"]
        
        # 1. Generate an inspiring title
        post["title"] = generate_inspiring_title(pid, original_content)
        
        # 2. Extract a clean core quote
        core_quote = extract_core_quote(original_content)
        
        # 3. Format as a warm, inspiring Southern Vietnamese script (approx 50-60 words total, perfect for 20s)
        # We select greetings and closings randomly or dynamically to add variety
        if pid % 4 == 0:
            greeting = "Dạ chào bạn nhen! "
            outro = " Mong rằng lời dạy này sẽ tiếp thêm chánh niệm cho bạn hôm nay nhen! Bấm Đăng Ký kênh nha!"
        elif pid % 4 == 1:
            greeting = "Chào bạn lành nhen! "
            outro = " Sống thiện lành để nhận lại quả ngọt bình an nhen! Nhấn Đăng Ký kênh để cùng học kinh lành nha!"
        elif pid % 4 == 2:
            greeting = "Dạ chào bạn nhen! "
            outro = " Kiên nhẫn và bao dung là chìa khóa mở lối hạnh phúc thực sự nhen! Bấm Đăng Ký kênh nhen!"
        else:
            greeting = "Chào buổi tối bạn nhen! "
            outro = " Hãy luôn nương tựa vào chính mình và chánh pháp nhen! Đăng Ký kênh để đồng hành cùng mình nhen!"
            
        script = f"{greeting}Đức Phật dạy trong Kinh Nikaya: '{core_quote}'{outro}"
        
        post["summary"] = script
        modified_count += 1
        
    # Save back
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully updated database. Modified {modified_count} posts. Total posts: {len(posts)}")

if __name__ == "__main__":
    process_all_posts()
