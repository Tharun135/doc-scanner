import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        
        await page.goto("http://127.0.0.1:5000/")
        
        print("Waiting for file input...")
        await page.set_input_files("input[type=file]", "data/siemens_rule_test.txt")
        
        print("Clicking upload...")
        await page.click("button >> text=Upload & Analyze")
        
        print("Waiting for original-content...")
        await page.wait_for_selector(".original-content", timeout=15000)
        
        print("Scraping results...")
        content_html = await page.inner_html(".original-content")
        
        with open("test_output.html", "w", encoding="utf-8") as f:
            f.write(content_html)
            
        print("Browser errors:", errors)
        await browser.close()
        print("Done!")

import nest_asyncio
nest_asyncio.apply()
asyncio.run(main())
