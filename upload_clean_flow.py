import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"
VIDEO_PATH = "static/output/post_1.mp4"
CAPTION = "Kinh Nikaya: Lối Sống Biết Đủ (SANTUTTHI) - Mở Khóa Bình An Gia Đình #Shorts #ThaoDuongTV"

def upload_clean_flow():
    print("Starting clean flow upload...")
    
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
        
        # Click "Turn on" for copyright checks instead of deleting DOM
        try:
            turn_on_btn = page.locator("button:has-text('Turn on')").first
            if turn_on_btn.is_visible():
                print("Clicking 'Turn on' button on copyright check modal...")
                turn_on_btn.click()
                page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Could not click 'Turn on': {e}")
            
        # Click "Got it" for any joyride guides instead of deleting DOM
        try:
            got_it_btn = page.locator("button:has-text('Got it')").first
            if got_it_btn.is_visible():
                print("Clicking 'Got it' button on guide...")
                got_it_btn.click()
                page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Could not click 'Got it': {e}")
            
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
        
        # Wait for natural redirect or success dialog
        print("Waiting for natural redirect (up to 45s)...")
        try:
            page.wait_for_url("**/tiktokstudio/content", timeout=45000)
            print("Successfully redirected to content list page!")
        except Exception as redirect_err:
            print(f"Redirect did not happen naturally: {redirect_err}")
            
        # Take screenshot of final result
        screenshot_path = os.path.join(OUTPUT_DIR, "clean_flow_final.png")
        page.screenshot(path=screenshot_path)
        print(f"Final screenshot saved to {screenshot_path}")
        print(f"Final URL: {page.url}")
        
        browser.close()

if __name__ == "__main__":
    upload_clean_flow()
