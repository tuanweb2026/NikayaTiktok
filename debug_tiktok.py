import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"

def debug_tiktok():
    print("Starting TikTok page debug...")
    
    if not os.path.exists(COOKIES_PATH):
        print("Cookies file not found.")
        return
        
    with open(COOKIES_PATH, 'r') as f:
        cookies_list = json.load(f)
        
    # Sanitize cookies for Playwright compatibility
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
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        context.add_cookies(sanitized_cookies)
        
        page = context.new_page()
        
        # Test the creator upload page
        url = "https://www.tiktok.com/creator-center/upload?from=upload"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(7000)
        
        print(f"Page URL: {page.url}")
        print(f"Page Title: {page.title()}")
        
        # Save screenshot
        screenshot_path = os.path.join(OUTPUT_DIR, "tiktok_debug.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Check inputs on the page
        inputs = page.query_selector_all("input[type='file']")
        print(f"Found {len(inputs)} file inputs on main page.")
        
        # Check if iframe exists
        iframes = page.query_selector_all("iframe")
        print(f"Found {len(iframes)} iframes on page.")
        for idx, iframe in enumerate(iframes):
            print(f"Iframe #{idx}: src={iframe.get_attribute('src') or 'none'}")
            
        browser.close()

if __name__ == "__main__":
    debug_tiktok()
