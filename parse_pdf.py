import pypdf
import json
import re
import os

PDF_PATH = "/Users/abc/Documents/Kenh_youtube/Nikaya_kinh/Nikaya_Kinh_Tat_Ca_Bai_Viet.pdf"
DB_PATH = "data/database.json"

def clean_text(text):
    # Remove footer lines
    text = re.sub(r'Kinh Nikaya - Tất cả bài viết\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'Trang \d+ / \d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove links
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove excessive whitespaces
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line and not line.startswith("See less")]
    return "\n".join(lines)

def summarize_text(text, target_words=45):
    """Summarize text to a single paragraph of approximately target_words."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' ').strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    current_words = []
    for s in sentences:
        s_words = s.split()
        if len(current_words) + len(s_words) <= target_words + 10:
            current_words.extend(s_words)
        else:
            if not current_words:
                current_words.extend(s_words[:target_words])
                return " ".join(current_words) + "..."
            break
            
    summary = " ".join(current_words)
    if not summary:
        # Fallback to simple truncation
        words = text.split()
        summary = " ".join(words[:target_words]) + "..." if len(words) > target_words else " ".join(words)
    return summary

def parse_pdf():
    print(f"Reading PDF from: {PDF_PATH}")
    if not os.path.exists(PDF_PATH):
        print("Error: PDF file not found!")
        return
        
    reader = pypdf.PdfReader(PDF_PATH)
    total_pages = len(reader.pages)
    print(f"Total pages to parse: {total_pages}")
    
    posts = []
    current_post = None
    
    # Pattern to match "Bài viết #123"
    post_header_pat = re.compile(r'^Bài viết #(\d+)', re.IGNORECASE)
    
    for page_idx in range(total_pages):
        page_text = reader.pages[page_idx].extract_text()
        if not page_text:
            continue
            
        lines = page_text.split('\n')
        for line in lines:
            line_strip = line.strip()
            header_match = post_header_pat.match(line_strip)
            
            if header_match:
                # Save previous post if exists
                if current_post:
                    cleaned = clean_text(current_post["raw_content"])
                    if cleaned and len(cleaned.split()) > 10:  # Ignore too short posts
                        current_post["content"] = cleaned
                        current_post["summary"] = summarize_text(cleaned)
                        posts.append(current_post)
                
                post_num = header_match.group(1)
                current_post = {
                    "id": int(post_num),
                    "title": f"Lời Phật Dạy #{post_num}",
                    "raw_content": "",
                    "content": "",
                    "summary": "",
                    "image_bg": "buddha_1.jpg", # default
                    "status": "pending" # pending, approved, rendered, uploaded
                }
            else:
                if current_post:
                    current_post["raw_content"] += line + "\n"
                    
    # Save the last post
    if current_post:
        cleaned = clean_text(current_post["raw_content"])
        if cleaned and len(cleaned.split()) > 10:
            current_post["content"] = cleaned
            current_post["summary"] = summarize_text(cleaned)
            posts.append(current_post)
            
    print(f"Extracted {len(posts)} posts from PDF.")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Save to JSON
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
        
    print(f"Database saved to {DB_PATH}")

if __name__ == "__main__":
    parse_pdf()
