import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"

def check_posts():
    print("Checking TikTok Studio posts...")
    
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
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        context.add_cookies(sanitized_cookies)
        
        page = context.new_page()
        
        url = "https://www.tiktok.com/tiktokstudio/posts"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(10000) # Wait 10s for posts list to load
        
        screenshot_path = os.path.join(OUTPUT_DIR, "tiktok_posts_check.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Print list content or text to see if the video is listed
        print("Page Text Content:")
        text = page.locator("body").text_content() or ""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for idx, line in enumerate(lines[:30]):
            print(f"{idx}: {line}")
            
        browser.close()

if __name__ == "__main__":
    check_posts()
