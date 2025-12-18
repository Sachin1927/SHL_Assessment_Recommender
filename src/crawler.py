import json
import os
import re
import time
from playwright.sync_api import sync_playwright

# --- CONFIGURATION: Force correct path and format ---
OUTPUT_FILE = os.path.join("data", "raw", "assessments.json")
TARGET_COUNT = 377

def scrape_shl_catalog():
    records = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print(" Navigating to SHL Catalog...")
        
        # INCREASED TIMEOUT to 60s and using domcontentloaded
        try:
            page.goto("https://www.shl.com/solutions/products/product-catalog/", wait_until="domcontentloaded", timeout=60000)
            print(" Waiting for product cards to appear...")
            page.wait_for_selector("a[href*='/view/']", timeout=6000)
        except Exception as e:
            print(f"Error loading page: {e}")
            browser.close()
            return

        # 1. Kill Cookie Banner
        try:
            page.locator("#onetrust-accept-btn-handler").click(timeout=3000)
            print(" Cookie banner dismissed.")
            page.wait_for_timeout(1000)
        except:
            pass

        stuck_counter = 0

        while len(records) < TARGET_COUNT:
            # --- STEP A: Scrape Current View ---
            cards = page.locator("a[href*='/view/']").all()
            start_count = len(records)
            
            for card in cards:
                try:
                    url = card.get_attribute("href")
                    if not url: continue
                    if not url.startswith("http"): url = "https://www.shl.com" + url

                    if url not in records:
                        text = card.inner_text().split('\n')
                        name = text[0].strip()
                        
                        # Filter out "Pre-packaged"
                        if "pre-packaged" in name.lower():
                            continue

                        if len(name) > 2:
                            records[url] = {
                                "name": name, 
                                "url": url, 
                                "description": text[1].strip() if len(text) > 1 else "Assessment for " + name,
                                "duration": 30, 
                                "adaptive_support": "No",
                                "remote_support": "Yes",
                                "test_type": ["Knowledge & Skills"] 
                            }
                except:
                    continue

            current_count = len(records)
            new_items = current_count - start_count
            print(f" Items Collected: {current_count} (Found {new_items} new this scroll)")

            if current_count >= TARGET_COUNT:
                print("Target count reached!")
                break

            # --- STEP B: Navigation ---
            page.keyboard.press("End")
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, -400)
            page.wait_for_timeout(500)

            button_regex = re.compile(r"Load More|Show More|Next", re.IGNORECASE)
            buttons = page.locator("a, button").filter(has_text=button_regex)
            
            clicked = False
            for i in range(buttons.count()):
                btn = buttons.nth(i)
                if btn.is_visible():
                    try:
                        if btn.is_disabled():
                            page.wait_for_timeout(2000)
                            continue
                        btn.click(force=True)
                        print(">> Clicked 'Load More'")
                        clicked = True
                        page.wait_for_timeout(3000) 
                        break 
                    except:
                        pass

            if not clicked:
                stuck_counter += 1
                print(f" No clickable button found. Stuck count: {stuck_counter}")
                page.mouse.wheel(0, 1000)
                page.wait_for_timeout(2000)

            if stuck_counter >= 5:
                print(" Completely Stuck. Saving what we have.")
                break

        browser.close()

    # --- SAVE LOGIC ---
    print(f" Saving {len(records)} records to {OUTPUT_FILE}...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Dump JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(records.values()), f, indent=4)
    
    print(f" Success! File saved at: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    scrape_shl_catalog()