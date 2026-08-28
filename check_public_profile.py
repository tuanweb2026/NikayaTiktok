import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "static/output"

def check_profile():
    print("Checking public profile page...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        url = "https://www.tiktok.com/@tuanweb2015"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(10000) # Wait 10s for posts grid to load
        
        screenshot_path = os.path.join(OUTPUT_DIR, "public_profile_check.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        print("Page Text Content:")
        text = page.locator("body").text_content() or ""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for idx, line in enumerate(lines[:30]):
            print(f"{idx}: {line}")
            
        browser.close()

if __name__ == "__main__":
    check_profile()
