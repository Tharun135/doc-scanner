#!/usr/bin/env python3
"""
More detailed debug of Microsoft URL processing
"""
import requests
from bs4 import BeautifulSoup
import html2text
import re

def test_microsoft_cleaning():
    url = "https://learn.microsoft.com/en-us/style-guide/welcome/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    print(f"🔍 Testing: {url}")
    
    # Fetch content
    response = requests.get(url, headers=headers, timeout=30)
    html = response.text
    print(f"Raw HTML length: {len(html)}")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    print(f"Initial soup body text length: {len(soup.get_text())}")
    
    # Step 1: Remove scripts/styles
    for tag in soup(["nav", "footer", "aside", "script", "style", "noscript"]):
        tag.decompose()
    print(f"After removing nav/footer/scripts: {len(soup.get_text())}")
    
    # Step 2: Remove navigation patterns (NEW PRECISE APPROACH)
    navigation_selectors = [
        "nav[class*='toc']",  # Table of contents nav
        "[role='navigation']",  # Elements with navigation role
        ".breadcrumb",  # Exact breadcrumb class (not partial match)
        ".sidebar", ".menu",  # Exact classes for sidebar and menu
        ".uhf-header", ".uhf-footer",  # Microsoft specific header/footer
        "[id*='uhf-header']", "[id*='uhf-footer']"  # Microsoft UHF by ID
    ]
    
    removed_count = 0
    for selector in navigation_selectors:
        elements = soup.select(selector)
        for element in elements:
            element.decompose()
            removed_count += 1
    print(f"Removed {removed_count} navigation elements, text length: {len(soup.get_text())}")
    
    # Step 3: Find main content
    main_content = None
    for selector in ['main', 'article', '[role="main"]', '.content', '[data-bi-name="content"]']:
        main_content = soup.select_one(selector)
        if main_content:
            text_len = len(main_content.get_text(strip=True))
            print(f"Found content with selector '{selector}': {text_len} chars")
            if text_len > 100:
                print(f"Using this content: {main_content.get_text(strip=True)[:200]}...")
                break
        else:
            print(f"No content found with selector: {selector}")
    
    if main_content and len(main_content.get_text(strip=True)) > 100:
        soup = BeautifulSoup(str(main_content), "html.parser")
        print(f"Using main content: {len(soup.get_text())} chars")
    elif soup.body:
        soup = BeautifulSoup(str(soup.body), "html.parser")
        print(f"Using body content: {len(soup.get_text())} chars")
    else:
        print("No body found, using full soup")
    
    # Step 4: Convert to markdown
    md_converter = html2text.HTML2Text()
    md_converter.ignore_links = False
    md_converter.body_width = 0
    md_converter.ignore_images = True
    
    markdown = md_converter.handle(str(soup))
    print(f"Raw markdown length: {len(markdown)}")
    
    # Step 5: Clean up
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = re.sub(r'[ \t]+\n', '\n', markdown)
    markdown = re.sub(r'^\s*\n', '', markdown, flags=re.MULTILINE)
    markdown = markdown.strip()
    
    print(f"Final cleaned markdown length: {len(markdown)}")
    if markdown:
        print(f"First 500 chars of markdown:")
        print("=" * 50)
        print(markdown[:500])
        print("=" * 50)
    else:
        print("❌ No markdown content!")
        
        # Debug: check what's in the soup after cleaning
        print(f"Debug - final soup text: '{soup.get_text()[:200]}...'")
        print(f"Debug - final soup HTML: '{str(soup)[:500]}...'")

if __name__ == "__main__":
    test_microsoft_cleaning()
