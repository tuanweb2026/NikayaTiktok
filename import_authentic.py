import json
import os

AUTHENTIC_PATH = "/Users/abc/.gemini/antigravity/scratch/1995lido_youtube_management/nikaya_30_authentic_posts.json"
DB_PATH = "data/database.json"

def import_authentic():
    print(f"Loading authentic posts from: {AUTHENTIC_PATH}")
    if not os.path.exists(AUTHENTIC_PATH):
        print("Error: Authentic posts file not found!")
        return
        
    with open(AUTHENTIC_PATH, 'r', encoding='utf-8') as f:
        auth_posts = json.load(f)
        
    print(f"Loaded {len(auth_posts)} authentic posts.")
    
    print(f"Loading current database from: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        posts = []
    else:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            posts = json.load(f)
            
    # Build dictionary of current posts keyed by ID
    posts_dict = {p["id"]: p for p in posts}
    
    # Import and overwrite or insert
    for item in auth_posts:
        pid = item["day"]
        
        # Select background image based on day to rotate them
        if pid % 3 == 1:
            bg = "buddha_1.jpg"
        elif pid % 3 == 2:
            bg = "buddha_2.jpg"
        else:
            bg = "buddha_3.jpg"
            
        posts_dict[pid] = {
            "id": pid,
            "title": item["title"],
            "content": item["script"],
            "summary": item["script"], # The script is already a beautiful 20s copy
            "image_bg": bg,
            "status": "pending"
        }
        
    # Convert back to list and sort by ID
    updated_posts = list(posts_dict.values())
    updated_posts.sort(key=lambda x: x["id"])
    
    # Save back to database.json
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_posts, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully imported and updated database. Total posts: {len(updated_posts)}")

if __name__ == "__main__":
    import_authentic()
