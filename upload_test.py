import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"
VIDEO_PATH = "static/output/post_1.mp4"

def test_upload():
    print("Testing upload process...")
    
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
        
    abs_video = os.path.abspath(VIDEO_PATH)
    if not os.path.exists(abs_video):
        print(f"Video not found at {abs_video}")
        return
        
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
        page.wait_for_timeout(7000)
        
        # Select input
        print("Locating file input...")
        file_input = page.locator("input[type='file']")
        print("Setting input files...")
        file_input.set_input_files(abs_video)
        
        print("Waiting 15 seconds for upload and form rendering...")
        page.wait_for_timeout(15000)
        
        # Take screenshot of the form
        screenshot_path = os.path.join(OUTPUT_DIR, "tiktok_upload_form.png")
        page.screenshot(path=screenshot_path)
        print(f"Form screenshot saved to {screenshot_path}")
        
        # Dump some elements info
        print("Checking for edit form elements...")
        divs = page.query_selector_all("div[contenteditable='true']")
        print(f"Found {len(divs)} contenteditable divs.")
        
        buttons = page.query_selector_all("button")
        for idx, btn in enumerate(buttons):
            text = btn.text_content() or ""
            if text.strip():
                print(f"Button #{idx}: text='{text.strip()}'")
                
        browser.close()

if __name__ == "__main__":
    test_upload()
