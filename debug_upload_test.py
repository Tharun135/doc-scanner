#!/usr/bin/env python3

import sys
sys.path.append('.')
import requests
import tempfile
import os

def test_upload_endpoint():
    # Test content with the problematic patterns
    test_content = '''# Test Document

You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

This sentence has **bold words** in the middle of it.

Here is a sentence with a [link](https://example.com) embedded.
'''

    print("=== TESTING UPLOAD ENDPOINT ===")
    print(f"Original content:\n{test_content}")
    print("\n" + "="*60)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Upload file to server
        with open(temp_file, 'rb') as f:
            files = {'file': ('test.md', f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"=== UPLOAD SUCCESSFUL ===")
            print(f"Number of sentences: {len(result.get('sentences', []))}")
            
            for i, sentence_data in enumerate(result.get('sentences', [])):
                print(f"\nSentence {i}:")
                print(f"  Text: '{sentence_data.get('sentence', '')}'")
                print(f"  HTML Segment: '{sentence_data.get('html_segment', 'None')}'")
                print(f"  Words: {sentence_data.get('words', [])}")
                print(f"  Start: {sentence_data.get('start', 'N/A')}")
                print(f"  End: {sentence_data.get('end', 'N/A')}")
                
                # Check if bold words are included
                sentence_text = sentence_data.get('sentence', '')
                if 'bold' in sentence_text.lower():
                    print(f"  *** CONTAINS 'bold': YES")
                    if '**' in sentence_text:
                        print(f"  *** STILL HAS MARKDOWN: YES")
                    else:
                        print(f"  *** MARKDOWN STRIPPED: YES")
            
            # Check for the "dex=" issue in HTML content
            content = result.get('content', '')
            print(f"\n=== CHECKING FOR 'dex=' ISSUE ===")
            if 'dex=' in content:
                print(f"FOUND 'dex=' in content!")
                # Find all occurrences
                import re
                matches = re.finditer(r'dex="[^"]*"', content)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]
                    print(f"Context: ...{context}...")
            else:
                print("No 'dex=' found in content")
            
            # Check highlighting patterns
            print(f"\n=== CHECKING HIGHLIGHTING PATTERNS ===")
            if 'data-sentence-index=' in content:
                import re
                highlight_matches = re.findall(r'<span[^>]*data-sentence-index="(\d+)"[^>]*>(.*?)</span>', content, re.DOTALL)
                print(f"Found {len(highlight_matches)} highlighted segments:")
                for idx, (sentence_idx, highlighted_text) in enumerate(highlight_matches):
                    # Clean up the text for display
                    clean_text = re.sub(r'<[^>]+>', '', highlighted_text).strip()
                    print(f"  Highlight {idx}: Sentence {sentence_idx} -> '{clean_text[:100]}...'")
            else:
                print("No highlighting found in content")
                
        else:
            print(f"=== UPLOAD FAILED ===")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    test_upload_endpoint()
