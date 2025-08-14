#!/usr/bin/env python3
"""
Debug script to see what HTML is being generated from markdown
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import markdown
from bs4 import BeautifulSoup

def debug_markdown_to_html():
    """Debug how markdown is converted to HTML and how text is extracted"""
    
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

For more information, see the [documentation](https://example.com/docs).

The interface shows ![icon](image.png) next to each option."""

    print("🔍 Debugging markdown to HTML conversion...")
    print("Input markdown:")
    print(repr(test_content))
    print("\n" + "="*50 + "\n")
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    html_content = md.convert(test_content)
    
    print("Generated HTML:")
    print(html_content)
    print("\n" + "="*50 + "\n")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    print("BeautifulSoup parsed structure:")
    print(soup.prettify())
    print("\n" + "="*50 + "\n")
    
    # Extract text using current method
    for script in soup(["script", "style"]):
        script.decompose()
    
    plain_text = soup.get_text(separator=" ")
    print("Extracted plain text:")
    print(repr(plain_text))
    print("\n" + "="*50 + "\n")
    
    # Find all text elements
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'li', 'blockquote'])
    
    print("Found text elements:")
    for i, element in enumerate(text_elements):
        print(f"Element {i}: {element.name}")
        print(f"  Text: {repr(element.get_text())}")
        print(f"  HTML: {repr(str(element))}")
        print()

if __name__ == "__main__":
    debug_markdown_to_html()
