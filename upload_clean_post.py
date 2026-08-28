import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIES_PATH = "data/tiktok_cookies.json"
OUTPUT_DIR = "static/output"
VIDEO_PATH = "static/output/post_1.mp4"
CAPTION = "Kinh Nikaya: Lối Sống Biết Đủ (SANTUTTHI) - Mở Khóa Bình An Gia Đình #Shorts #ThaoDuongTV"

def upload_clean_post():
    print("Starting clean upload and post flow...")
    
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
        
        # Dismiss copyright check modal by clicking Cancel inside the modal
        try:
            # The copyright modal cancel button
            cancel_btn = page.locator("div[role='dialog'] button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                print("Clicking modal Cancel button...")
                cancel_btn.click()
                page.wait_for_timeout(1000)
            else:
                # Fallback to general cancel button if it is in view
                cancel_btn_general = page.locator("button:has-text('Cancel')").first
                if cancel_btn_general.is_visible():
                    print("Clicking general Cancel button...")
                    cancel_btn_general.click()
                    page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Could not dismiss copyright modal: {e}")
            
        # Click "Got it" for any joyride guides
        try:
            got_it_btn = page.locator("button:has-text('Got it')").first
            if got_it_btn.is_visible():
                print("Clicking 'Got it' button...")
                got_it_btn.click()
                page.wait_for_timeout(1000)
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
        
        # Scroll down
        print("Scrolling down...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # Click Post
        print("Clicking Post button...")
        post_btn = page.locator("[data-e2e='post_video_button']").first
        post_btn.click()
        page.wait_for_timeout(3000)
        
        # Dismiss any confirmation exit modal that might pop up
        try:
            exit_btn = page.locator("button:has-text('Exit')").first
            if exit_btn.is_visible():
                print("Clicking Exit to confirm navigation...")
                exit_btn.click()
                page.wait_for_timeout(5000)
        except Exception as e:
            print(f"Exit button handling info: {e}")
            
        # Wait to ensure redirect completed and page rendered
        print("Waiting 10s for page redirection to settle...")
        page.wait_for_timeout(10000)
        
        # Take screenshot of final result
        screenshot_path = os.path.join(OUTPUT_DIR, "clean_post_final.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        print(f"Final URL: {page.url}")
        
        browser.close()

if __name__ == "__main__":
    upload_clean_post()
