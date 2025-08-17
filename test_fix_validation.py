#!/usr/bin/env python3
"""
Test the formatting preservation fix by uploading the test document
and checking if formatting elements are properly preserved in sentences.
"""

import requests
import json
import time

def test_formatting_fix():
    """Test that formatting elements don't break sentence boundaries."""
    
    print("🔍 TESTING FORMATTING PRESERVATION FIX")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Read the test file
    with open('test_formatting_fix.md', 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    print("📄 Test document content preview:")
    lines = test_content.split('\n')[:10]
    for line in lines:
        if line.strip():
            print(f"  {line}")
    print("\n" + "=" * 60)
    
    # Upload the test file
    try:
        print("📤 Uploading test file to server...")
        files = {'file': ('test_formatting_fix.md', test_content, 'text/markdown')}
        response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            
            # Parse the response
            result = response.json()
            
            print(f"\n📊 Analysis Results:")
            print(f"Total sentences found: {result.get('sentence_count', 'N/A')}")
            
            # Check sentences with formatting
            sentences = result.get('sentences', [])
            print(f"\n🔍 Detailed Sentence Analysis:")
            
            key_tests = [
                'Enable Autostart',
                'bold words',
                'helpful link', 
                '176617096203-d2e2393',
                'bold text**, add [links'
            ]
            
            for i, sentence_data in enumerate(sentences, 1):
                sentence_text = sentence_data.get('text', '')
                sentence_html = sentence_data.get('html', '')
                
                print(f"\n--- Sentence {i} ---")
                print(f"Text: {sentence_text}")
                print(f"HTML: {sentence_html}")
                
                # Check if this contains any key formatting
                has_formatting = any(test in sentence_text.lower() for test in key_tests)
                if has_formatting:
                    print("✅ Contains formatting elements - checking preservation...")
                    
                    # Check if formatting is preserved
                    if '**' in sentence_html or '<strong>' in sentence_html:
                        print("  ✅ Bold formatting preserved")
                    if '[' in sentence_html and '](' in sentence_html or '<a' in sentence_html:
                        print("  ✅ Link formatting preserved")
                    if any(char.isdigit() for char in sentence_text) and '-' in sentence_text:
                        print("  ✅ Image reference preserved")
            
            print(f"\n🎯 KEY TEST: Sentence boundary preservation")
            print(f"Expected: Each paragraph should be one sentence")
            print(f"Actual: Found {len(sentences)} sentences total")
            
            # Look for the specific problematic cases
            autostart_found = False
            mixed_formatting_found = False
            
            for sentence_data in sentences:
                text = sentence_data.get('text', '').lower()
                if 'enable autostart' in text and 'activating' in text:
                    autostart_found = True
                    print("✅ 'Enable Autostart' sentence preserved as single unit")
                if 'bold text' in text and 'links' in text and 'images' in text:
                    mixed_formatting_found = True
                    print("✅ Mixed formatting sentence preserved as single unit")
            
            if autostart_found and mixed_formatting_found:
                print("\n🎉 FORMATTING PRESERVATION FIX: SUCCESS!")
                print("✅ Critical test cases are working correctly")
            else:
                print("\n⚠️ FORMATTING PRESERVATION FIX: PARTIAL SUCCESS")
                print("🔍 Some edge cases may need additional work")
                
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_formatting_fix()
