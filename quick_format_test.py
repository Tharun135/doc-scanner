#!/usr/bin/env python3
"""
Simple test to verify our fixes are working
"""

import requests
import json
import tempfile
import os

def test_formatting_quickly():
    """Quick test via API"""
    
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

For more information, see the [documentation](https://example.com/docs).

The interface shows ![icon](image.png) next to each option."""

    print("🧪 Testing formatting preservation...")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_path = f.name
    
    try:
        # Upload
        with open(temp_path, 'rb') as f:
            response = requests.post('http://127.0.0.1:5000/upload', 
                                   files={'file': ('test.md', f, 'text/markdown')})
        
        if response.status_code == 200:
            data = response.json()
            sentences = data.get('sentences', [])
            
            print(f"\n✅ Got {len(sentences)} sentences")
            
            for i, sent in enumerate(sentences):
                print(f"\nSentence {i+1}:")
                print(f"  Text: {sent['sentence']}")
                
                if 'html_text' in sent and sent['html_text'] != sent['sentence']:
                    print(f"  HTML: {sent['html_text']}")
                    print("  ✅ HTML preserved!")
                else:
                    print("  ❌ No HTML preservation detected")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    finally:
        os.unlink(temp_path)

if __name__ == "__main__":
    test_formatting_quickly()
