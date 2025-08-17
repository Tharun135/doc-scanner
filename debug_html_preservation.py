#!/usr/bin/env python3
"""
Direct test of HTML preservation logic
"""

from bs4 import BeautifulSoup
import sys
sys.path.append('d:/doc-scanner')

def test_html_preservation():
    """Test HTML preservation directly"""
    
    # Test HTML content
    html_content = '''<p>You can choose to set any project to Autostart mode by activating the <strong>Enable Autostart</strong> option.</p>'''
    
    print("🔍 TESTING HTML PRESERVATION")
    print("=" * 50)
    print("Original HTML:")
    print(html_content)
    print()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find paragraph elements
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    paragraph_blocks = []
    
    for element in text_elements:
        # Extract text like the app does
        block_text = ""
        for content in element.contents:
            if hasattr(content, 'get_text'):
                # This is an HTML element
                block_text += content.get_text(separator=" ")
            else:
                # This is plain text
                block_text += str(content)
        
        if block_text.strip():
            block_text = block_text.strip()
            paragraph_blocks.append({
                'plain': block_text,
                'html': str(element)
            })
    
    print("📊 Paragraph blocks created:")
    for i, block in enumerate(paragraph_blocks, 1):
        print(f"Block {i}:")
        print(f"  Plain: '{block['plain']}'")
        print(f"  HTML: '{block['html']}'")
        print()
    
    # Test what happens when we store the HTML
    if paragraph_blocks:
        test_block = paragraph_blocks[0]
        html_block = test_block['html']
        print(f"HTML block content: '{html_block}'")
        print(f"Contains formatting: {'<strong>' in html_block}")

if __name__ == "__main__":
    test_html_preservation()
