import os
import time
from playwright.sync_api import sync_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "verification_screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_verification_screenshots():
    print("[INFO] Launching Playwright Chromium headless browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        # 1. Overview Page & Real-time Insights
        print("[INFO] Navigating to Overview Page...")
        page.goto("http://localhost:8501", timeout=60000)
        time.sleep(5)  # Wait for initial Streamlit render & LLM insights
        
        # Take screenshot of Overview + AI Insights
        path_insights = os.path.join(OUTPUT_DIR, "01_realtime_insights.png")
        page.screenshot(path=path_insights, full_page=True)
        print(f"[SUCCESS] Saved screenshot: {path_insights}")
        
        # 2. Trend & Comparative Analytics Page
        print("[INFO] Navigating to Trend Analytics Page...")
        page.get_by_text("Trend & Comparative Analytics").click()
        time.sleep(4)
        path_trends = os.path.join(OUTPUT_DIR, "02_trend_analysis.png")
        page.screenshot(path=path_trends, full_page=True)
        print(f"[SUCCESS] Saved screenshot: {path_trends}")

        # 3. Predictive Enrollment Modeling Page
        print("[INFO] Navigating to Predictive Modeling Page...")
        page.get_by_text("Predictive Enrollment Modeling").click()
        time.sleep(4)
        path_predictive = os.path.join(OUTPUT_DIR, "03_predictive_enrollment.png")
        page.screenshot(path=path_predictive, full_page=True)
        print(f"[SUCCESS] Saved screenshot: {path_predictive}")

        # 4. Generative AI / Natural Language Query Assistant Page
        print("[INFO] Navigating to AI Assistant Page...")
        page.get_by_text("AI Assistant (NL Query)").click()
        time.sleep(4)
        
        # Click suggested question chip
        page.get_by_text("Which districts have the highest dropout rate in engineering?").click()
        time.sleep(5)  # Wait for Groq LLM completion and chart render
        
        path_nl_query = os.path.join(OUTPUT_DIR, "04_generative_ai_nl_query.png")
        page.screenshot(path=path_nl_query, full_page=True)
        print(f"[SUCCESS] Saved screenshot: {path_nl_query}")

        browser.close()
        print("=== ALL SCREENSHOTS CAPTURED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_verification_screenshots()
