#!/usr/bin/env python3
"""
Test script to verify formatting preservation in sentences
"""

import requests
import json

def test_formatting_preservation():
    """Test that bold, links, and images are preserved in sentences"""
    
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

For more information, see the [documentation](https://example.com/docs).

The interface shows ![icon](image.png) next to each option."""

    print("🔍 Testing formatting preservation...")
    print("Input text:")
    print(test_content)
    print("\n" + "="*50 + "\n")
    
    # Create a temporary markdown file and upload it
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # Upload the file to the server
        with open(temp_file_path, 'rb') as f:
            files = {'file': (os.path.basename(temp_file_path), f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📊 Processing results:")
            print(f"Total sentences found: {len(result['sentences'])}")
            print("\n" + "="*50 + "\n")
            
            # Check each sentence
            for i, sentence in enumerate(result['sentences'], 1):
                print(f"Sentence {i}:")
                print(f"  Text: {sentence['sentence']}")
                
                # Check if html_text exists and has formatting
                if 'html_text' in sentence:
                    print(f"  HTML: {sentence['html_text']}")
                    
                    # Check for preserved formatting
                    has_bold = '**' in sentence['html_text'] or '<strong>' in sentence['html_text'] or '<b>' in sentence['html_text']
                    has_link = '[' in sentence['html_text'] and '](' in sentence['html_text'] or '<a ' in sentence['html_text']
                    has_image = '![' in sentence['html_text'] or '<img ' in sentence['html_text']
                    
                    formatting_preserved = has_bold or has_link or has_image
                    print(f"  Formatting preserved: {formatting_preserved}")
                    
                    if formatting_preserved:
                        print("  ✅ Formatting elements found!")
                    else:
                        print("  ❌ No formatting elements found")
                else:
                    print("  ❌ No html_text property found")
                    
                print()
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_formatting_preservation()
