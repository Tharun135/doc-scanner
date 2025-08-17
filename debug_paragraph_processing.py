#!/usr/bin/env python3
"""
Simple debug script to test HTML paragraph processing
"""

import sys
sys.path.append('d:/doc-scanner')

import tempfile
import os
import requests
import json

def test_paragraph_processing():
    """Test how paragraphs with formatting are being processed"""
    
    # Simple test content with formatting
    test_content = '''You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.'''

    print("🔍 TESTING PARAGRAPH PROCESSING")
    print("=" * 50)
    print("Input content:")
    print(test_content)
    print()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # Upload the file to the server
        print("📤 Uploading to server...")
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test.md', f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📊 Server Response:")
            print(f"Original content: {result['content']}")
            print()
            
            for i, sentence in enumerate(result['sentences'], 1):
                print(f"Sentence {i}:")
                print(f"  Plain text: '{sentence['sentence']}'")
                print(f"  HTML segment: '{sentence['html_segment']}'")
                print(f"  Content: '{sentence['content']}'")
                print()
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    test_paragraph_processing()
