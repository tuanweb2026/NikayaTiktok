import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

DB_PATH = "data/database.json"
COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"

def upload_to_tiktok(post_id):
    print(f"Starting TikTok Upload for Post ID: {post_id}")
    
    # 1. Check database for post
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return False
        
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        posts = json.load(f)
        
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        print(f"Post {post_id} not found in database.")
        return False
        
    video_path = os.path.abspath(os.path.join(OUTPUT_DIR, f"post_{post_id}.mp4"))
    if not os.path.exists(video_path):
        print(f"Video file not found: {video_path}")
        return False
        
    # Generate caption
    # Truncate content for caption if it's too long, add tags
    short_content = post["content"][:80] + "..." if len(post["content"]) > 80 else post["content"]
    caption = f"Lời Phật Dạy: {short_content}\n\nNhấn Đăng Ký kênh Thảo Dương TV (@tuanweb2015) để cùng gieo duyên lành nhen! 🙏\n\n#phatgiao #kinhnikaya #loiphatday #thaoduongtv #tuanweb2015 #nhacthien #anlac #xuhuong"
    
    print(f"Video path: {video_path}")
    print(f"Caption: {caption}")
    
    # 2. Check cookies file
    if not os.path.exists(COOKIES_PATH):
        print(f"Cookies file {COOKIES_PATH} not found. Please log in first.")
        return False
        
    with open(COOKIES_PATH, 'r') as f:
        cookies_list = json.load(f)
        
    # Sanitize cookies for Playwright compatibility
    sanitized_cookies = []
    for cookie in cookies_list:
        clean_cookie = cookie.copy()
        
        # Convert expirationDate to expires
        if "expirationDate" in clean_cookie:
            clean_cookie["expires"] = clean_cookie.pop("expirationDate")
            
        # Clean sameSite values
        if "sameSite" in clean_cookie:
            val = str(clean_cookie["sameSite"]).lower()
            if val in ["strict", "lax", "none"]:
                clean_cookie["sameSite"] = val.capitalize()
            else:
                del clean_cookie["sameSite"]
                
        sanitized_cookies.append(clean_cookie)
        
    # 3. Initialize Playwright
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True) # Set to False for debugging if needed
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Add cookies
        print("Adding cookies to session...")
        context.add_cookies(sanitized_cookies)
        
        page = context.new_page()
        
        # Go to upload page
        upload_url = "https://www.tiktok.com/creator-center/upload?from=upload"
        print(f"Navigating to {upload_url}...")
        page.goto(upload_url, wait_until="domcontentloaded")
        
        # Wait a moment for page to load JS
        page.wait_for_timeout(5000)
        
        # Check if we are redirected to login (indicating invalid cookies)
        if "login" in page.url:
            print("Error: Cookies are expired or invalid. Please update data/tiktok_cookies.json.")
            browser.close()
            return False
            
        print("Uploading file... Searching for file input")
        
        # Locate the file input directly on the main page (no iframe, state='attached' because it is hidden)
        file_input = page.wait_for_selector("input[type='file']", state="attached")
        file_input.set_input_files(video_path)
        print("Video uploaded. Waiting for processing...")
        page.wait_for_timeout(10000) # Wait 10 seconds for upload/render preview
        
        # Dismiss copyright check modal by clicking Cancel inside the modal
        try:
            cancel_btn = page.locator("div[role='dialog'] button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                print("Clicking modal Cancel button...")
                cancel_btn.click()
                page.wait_for_timeout(1000)
            else:
                cancel_btn_general = page.locator("button:has-text('Cancel')").first
                if cancel_btn_general.is_visible():
                    print("Clicking general Cancel button...")
                    cancel_btn_general.click()
                    page.wait_for_timeout(1000)
        except Exception as modal_err:
            print(f"Modal check info: {modal_err}")
            
        # Click "Got it" for any joyride guides
        try:
            got_it_btn = page.locator("button:has-text('Got it')").first
            if got_it_btn.is_visible():
                print("Clicking 'Got it' button...")
                got_it_btn.click()
                page.wait_for_timeout(1000)
        except Exception as joyride_err:
            print(f"Joyride cleanup info: {joyride_err}")
            
        # Locate caption input (on the main page)
        print("Writing caption...")
        editor = page.wait_for_selector("div[contenteditable='true']")
        editor.click()
        # Clear existing text
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        # Type the caption
        editor.fill(caption)
        page.wait_for_timeout(2000)
        
        # Scroll down to bring Post button into view
        print("Scrolling down...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # Wait for the "Post" / "Đăng" button to become active
        print("Locating Post button...")
        post_btn = page.locator("[data-e2e='post_video_button']").first
        
        # Click Post
        print("Clicking Post button...")
        post_btn.click()
        page.wait_for_timeout(3000)
        
        # Dismiss any confirmation exit modal that might pop up during redirect
        try:
            exit_btn = page.locator("button:has-text('Exit')").first
            if exit_btn.is_visible():
                print("Clicking Exit to confirm upload/navigation...")
                exit_btn.click()
                page.wait_for_timeout(3000)
        except Exception as exit_err:
            print(f"Exit popup handle info: {exit_err}")
            
        # Wait for success dialog / redirect
        print("Waiting for page redirection to settle...")
        page.wait_for_timeout(10000)
        
        print("Video uploaded successfully!")
        
        # 4. Update post status in DB
        post["status"] = "uploaded"
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)
            
        browser.close()
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            pid = int(sys.argv[1])
            success = upload_to_tiktok(pid)
            if success:
                print("Success")
                sys.exit(0)
            else:
                print("Failed")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Usage: python3 upload_tiktok.py <post_id>")
