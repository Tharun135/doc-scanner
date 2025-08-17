#!/usr/bin/env python3
"""
Debug script to investigate the sentence splitting issue with formatting
"""

import requests
import tempfile
import os
from bs4 import BeautifulSoup
import json

def test_formatting_issue():
    """Test how sentences with formatting are being processed"""
    
    # Test content with problematic patterns
    test_content = '''# Test Document for Formatting Issues

You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

This sentence has **bold words** in the middle and should work perfectly.

Here is a sentence with a [helpful link](https://example.com) that should not break.

This sentence contains an image reference 176617096203-d2e2393 that should not split.

**Bold text at start** of sentence works fine.

Multiple formatting: you can use **bold text**, add [links](https://test.com), and reference images 12345-abcde in one sentence.
'''

    print("🔍 TESTING FORMATTING ISSUE")
    print("=" * 60)
    print("Test content:")
    print(test_content)
    print("\n" + "="*60)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # Upload the file to the server
        print("📤 Uploading test file to server...")
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test.md', f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📊 Server Response Analysis:")
            print(f"Total sentences found: {len(result['sentences'])}")
            if 'total_issues' in result:
                print(f"Total issues found: {result['total_issues']}")
            else:
                total_issues = sum(len(s.get('feedback', [])) for s in result['sentences'])
                print(f"Total issues found: {total_issues}")
            print("\n" + "="*50 + "\n")
            
            # Analyze each sentence
            for i, sentence in enumerate(result['sentences'], 1):
                print(f"Sentence {i}:")
                print(f"  Plain: '{sentence['sentence']}'")
                
                # Check html_segment
                if 'html_segment' in sentence:
                    print(f"  HTML Segment: '{sentence['html_segment']}'")
                else:
                    print("  ❌ No html_segment property")
                
                # Check content
                if 'content' in sentence:
                    print(f"  Content: '{sentence['content']}'")
                else:
                    print("  ❌ No content property")
                
                # Check length
                print(f"  Length: {len(sentence['sentence'])} chars")
                
                # Check for feedback
                if sentence.get('feedback'):
                    print(f"  Issues: {len(sentence['feedback'])} found")
                    for issue in sentence['feedback']:
                        print(f"    - {issue.get('message', 'No message')}")
                else:
                    print("  Issues: None")
                
                print()
                
            print("🎯 Expected Sentences:")
            print("1. 'You can choose to set any project to Autostart mode by activating the Enable Autostart option.'")
            print("2. 'This sentence has bold words in the middle and should work perfectly.'")
            print("3. 'Here is a sentence with a helpful link that should not break.'")
            print("4. 'This sentence contains an image reference 176617096203-d2e2393 that should not split.'")
            print("5. 'Bold text at start of sentence works fine.'")
            print("6. 'Multiple formatting: you can use bold text, add links, and reference images 12345-abcde in one sentence.'")
            print(f"\nExpected: 6 sentences, Got: {len(result['sentences'])} sentences")
            
            # Save detailed response for analysis
            with open('debug_formatting_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("\n💾 Detailed response saved to 'debug_formatting_response.json'")
                
        else:
            print(f"❌ Server Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

def analyze_html_conversion():
    """Analyze how markdown gets converted to HTML"""
    import sys
    sys.path.append('d:/doc-scanner')
    from app.app import parse_file
    
    print("\n🔍 ANALYZING HTML CONVERSION")
    print("=" * 40)
    
    test_content = '''You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        # Parse markdown to HTML
        with open(temp_file_path, 'rb') as f:
            mock_file = type('MockFile', (), {
                'filename': 'test.md',
                'read': f.read
            })()
            html_content = parse_file(mock_file)
        
        print("Original markdown:")
        print(test_content)
        print("\nConverted HTML:")
        print(html_content)
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("\nExtracted plain text (with space separator):")
        plain_text_space = soup.get_text(separator=" ")
        print(f"'{plain_text_space}'")
        
        print("\nExtracted plain text (with newline separator):")
        plain_text_newline = soup.get_text(separator="\n")
        print(f"'{plain_text_newline}'")
        
        print("\n🔍 This shows how separator affects text extraction")
        
    finally:
        os.unlink(temp_file_path)

if __name__ == "__main__":
    try:
        # First test the HTML conversion
        analyze_html_conversion()
        
        # Then test the full processing
        test_formatting_issue()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
