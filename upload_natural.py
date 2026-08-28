import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"
VIDEO_PATH = "static/output/post_1.mp4"
CAPTION = "Kinh Nikaya: Lối Sống Biết Đủ (SANTUTTHI) - Mở Khóa Bình An Gia Đình #Shorts #ThaoDuongTV"

def upload_natural():
    print("Starting natural upload process...")
    
    if not os.path.exists(COOKIES_PATH):
        print("Cookies file not found.")
        return
        
    with open(COOKIES_PATH, 'r') as f:
        cookies_list = json.load(f)
        
    # Sanitize cookies
    sanitized_cookies = []
    for cookie in cookies_list:
        clean_cookie = cookie.copy()
        if "expirationDate" in clean_cookie:
            clean_cookie["expires"] = clean_cookie.pop("expirationDate")
        if "sameSite" in clean_cookie:
            val = str(clean_cookie["sameSite"]).lower()
            if val in ["strict", "lax", "none"]:
                clean_cookie["sameSite"] = val.capitalize()
            else:
                del clean_cookie["sameSite"]
        sanitized_cookies.append(clean_cookie)
        
    abs_video = os.path.abspath(VIDEO_PATH)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        context.add_cookies(sanitized_cookies)
        
        page = context.new_page()
        
        url = "https://www.tiktok.com/tiktokstudio/upload?from=upload"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        
        # Select tệp
        print("Uploading file...")
        file_input = page.wait_for_selector("input[type='file']", state="attached")
        file_input.set_input_files(abs_video)
        page.wait_for_timeout(10000)
        
        # Force remove overlays, joyrides, and portals (TUXModal and joyride guides) from DOM using JS
        print("Removing guide overlays and modals from DOM...")
        page.evaluate("""
            document.querySelectorAll('[class*="joyride"], [id*="joyride"], [id*="portal"], [data-floating-ui-portal], .TUXModal-overlay, [class*="Modal"]').forEach(el => el.remove());
            document.body.style.overflow = "auto";
            document.documentElement.style.overflow = "auto";
        """)
        page.wait_for_timeout(2000)
        
        # Fill caption
        print("Writing caption...")
        editor = page.wait_for_selector("div[contenteditable='true']")
        editor.click()
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        editor.fill(CAPTION)
        page.wait_for_timeout(2000)
        
        # Click Post
        print("Clicking Post button...")
        post_btn = page.wait_for_selector("button:has-text('Post')")
        post_btn.click()
        
        # Wait for natural redirect to /content
        print("Waiting for redirect to content list page (up to 60s)...")
        try:
            page.wait_for_url("**/tiktokstudio/content", timeout=60000)
            print("Successfully redirected naturally!")
        except Exception as redirect_err:
            print(f"Redirect timeout or error: {redirect_err}")
            page.screenshot(path=os.path.join(OUTPUT_DIR, "natural_redirect_failed.png"))
            
        print("Taking final confirmation screenshot...")
        page.wait_for_timeout(5000)
        page.screenshot(path=os.path.join(OUTPUT_DIR, "natural_final.png"))
        print(f"Final URL: {page.url}")
        
        browser.close()

if __name__ == "__main__":
    upload_natural()
