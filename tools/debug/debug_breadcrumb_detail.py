#!/usr/bin/env python3
"""
Debug what the breadcrumb selector is matching
"""
import requests
from bs4 import BeautifulSoup

def debug_breadcrumb_selector():
    url = "https://learn.microsoft.com/en-us/style-guide/welcome/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove basic tags first
    for tag in soup(["nav", "footer", "aside", "script", "style", "noscript"]):
        tag.decompose()
    
    print(f"After basic cleanup: {len(soup.get_text())} chars")
    
    # Find elements matching breadcrumb
    breadcrumb_elements = soup.select("[class*='breadcrumb']")
    print(f"Found {len(breadcrumb_elements)} elements matching [class*='breadcrumb']")
    
    for i, element in enumerate(breadcrumb_elements):
        print(f"\nElement {i+1}:")
        print(f"  Tag: {element.name}")
        print(f"  Classes: {element.get('class', [])}")
        print(f"  Text length: {len(element.get_text())}")
        print(f"  First 200 chars: {element.get_text()[:200]}...")
        print(f"  HTML snippet: {str(element)[:200]}...")

if __name__ == "__main__":
    debug_breadcrumb_selector()
