#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

# Test the problematic sentence in different formats
test_sentence = "If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files."

# Test as HTML (like the app would pass it)
html_content = f"<p>{test_sentence}</p>"

print("Testing URL detection with different content formats:\n")

print(f"1. Plain text: {test_sentence}")
print(f"2. HTML content: {html_content}")
print()

try:
    from app.rules.cross_references import check
    
    print("Testing plain text:")
    suggestions1 = check(test_sentence)
    print(f"Suggestions: {suggestions1}")
    print()
    
    print("Testing HTML content:")
    suggestions2 = check(html_content)
    print(f"Suggestions: {suggestions2}")
    print()
    
    # Also test with BeautifulSoup processing like the rule does
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    print(f"Extracted text from HTML: {text_content}")
    
    # Test the URL pattern directly on extracted text
    import re
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
    urls_found = re.findall(url_pattern, text_content, flags=re.IGNORECASE)
    print(f"URLs found in extracted text: {urls_found}")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Cannot test the actual rule - testing regex directly")
    
    import re
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
    
    urls_plain = re.findall(url_pattern, test_sentence, flags=re.IGNORECASE)
    print(f"URLs in plain text: {urls_plain}")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    text_from_html = soup.get_text()
    urls_html = re.findall(url_pattern, text_from_html, flags=re.IGNORECASE)
    print(f"URLs in HTML-extracted text: {urls_html}")
    
except Exception as e:
    print(f"Other error: {e}")
