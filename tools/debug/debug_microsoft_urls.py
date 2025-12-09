#!/usr/bin/env python3
"""
Debug script to check what's happening with Microsoft URLs
"""
import requests
from bs4 import BeautifulSoup
import html2text

MICROSOFT_URLS = [
    "https://learn.microsoft.com/en-us/style-guide/welcome/",
    "https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips",
    "https://learn.microsoft.com/en-us/style-guide/urls-web-addresses",
    "https://learn.microsoft.com/en-us/style-guide/text-formatting/formatting-common-text-elements",
    "https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

def debug_url(url):
    print(f"\n🔍 Debugging: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Raw content length: {len(response.text)}")
        
        if response.text:
            # Check if it's HTML
            if 'html' in response.headers.get('Content-Type', '').lower():
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for main content areas
                main_content = soup.find('main') or soup.find('article') or soup.find('[role="main"]')
                if main_content:
                    print(f"Main content found: {len(str(main_content))} chars")
                else:
                    print("No main content area found")
                
                # Check for JavaScript requirements
                scripts = soup.find_all('script')
                print(f"Script tags: {len(scripts)}")
                
                # Look for specific content indicators
                body = soup.find('body')
                if body:
                    text_content = body.get_text(strip=True)
                    print(f"Body text length: {len(text_content)}")
                    if text_content:
                        print(f"First 200 chars: {text_content[:200]}")
                else:
                    print("No body tag found")
                    
        else:
            print("Empty response body")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    for url in MICROSOFT_URLS:
        debug_url(url)
