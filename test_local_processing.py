#!/usr/bin/env python3
"""
Test the fixed formatting preservation without relying on server
"""

import sys
sys.path.append('d:/doc-scanner')

from app.app import parse_file
import tempfile
import markdown
from bs4 import BeautifulSoup

def test_local_processing():
    """Test the processing logic locally"""
    
    test_content = '''You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.'''
    
    print("🔍 TESTING LOCAL PROCESSING")
    print("=" * 50)
    print("Input markdown:")
    print(test_content)
    print()
    
    # Step 1: Convert markdown to HTML (like parse_file does)
    html_content = markdown.markdown(test_content)
    print("Step 1 - HTML conversion:")
    print(html_content)
    print()
    
    # Step 2: Parse with BeautifulSoup (like app.py does)
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Step 3: Extract paragraph blocks (like app.py does)
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'li', 'blockquote'])
    
    paragraph_blocks = []
    
    for element in text_elements:
        # Extract text with careful handling of inline elements
        block_text = ""
        for content in element.contents:
            if hasattr(content, 'get_text'):
                # This is an HTML element
                block_text += content.get_text(separator=" ")
            else:
                # This is plain text
                block_text += str(content)
        
        # Clean and normalize the block text
        if block_text.strip():
            block_text = block_text.strip()
            # Only add if it's substantial content (not just punctuation)
            if len(block_text.strip()) > 2:
                paragraph_blocks.append({
                    'plain': block_text,
                    'html': str(element)  # Store both plain and HTML
                })
    
    print("Step 3 - Paragraph blocks:")
    for i, block in enumerate(paragraph_blocks, 1):
        print(f"Block {i}:")
        print(f"  Plain: '{block['plain']}'")
        print(f"  HTML: '{block['html']}'")
        print(f"  Contains formatting: {'<strong>' in block['html']}")
        print()
    
    # Step 4: Simulate sentence processing
    if paragraph_blocks:
        block = paragraph_blocks[0]
        html_block = block['html']
        plain_block = block['plain']
        
        print("Step 4 - Sentence would get:")
        print(f"  Plain sentence: '{plain_block}'")
        print(f"  HTML block: '{html_block}'")
        print(f"  HTML preserves formatting: {'<strong>' in html_block}")

if __name__ == "__main__":
    test_local_processing()
