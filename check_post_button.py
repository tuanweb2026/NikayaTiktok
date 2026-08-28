import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"
VIDEO_PATH = "static/output/post_1.mp4"
CAPTION = "Kinh Nikaya: Lối Sống Biết Đủ (SANTUTTHI) - Mở Khóa Bình An Gia Đình #Shorts #ThaoDuongTV"

def check_post_button():
    print("Checking Post button state...")
    
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
            viewport={"width": 1280, "height": 1000}
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
        
        # Dismiss copyright check modal naturally
        try:
            turn_on_btn = page.locator("button:has-text('Turn on')").first
            if turn_on_btn.is_visible():
                turn_on_btn.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass
            
        # Clean guide overlays
        page.evaluate("document.querySelectorAll('[class*=\"joyride\"], [id*=\"joyride\"], [id*=\"portal\"]').forEach(el => el.remove())")
        page.wait_for_timeout(1000)
        
        # Fill caption
        print("Writing caption...")
        editor = page.wait_for_selector("div[contenteditable='true']")
        editor.click()
        page.keyboard.press("Meta+A")
        page.keyboard.press("Backspace")
        editor.fill(CAPTION)
        page.wait_for_timeout(2000)
        
        # Scroll to bottom
        print("Scrolling to bottom...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # Take screenshot of the bottom area
        screenshot_path = os.path.join(OUTPUT_DIR, "tiktok_post_button_area.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        # Inspect Post button
        post_btn = page.locator("button:has-text('Post')").first
        if post_btn.is_visible():
            is_disabled = post_btn.get_attribute("disabled") is not None
            print(f"Post button is visible. Disabled state: {is_disabled}")
        else:
            print("Post button is NOT visible at the bottom!")
            
        browser.close()

if __name__ == "__main__":
    check_post_button()
