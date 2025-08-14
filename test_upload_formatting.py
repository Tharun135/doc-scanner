#!/usr/bin/env python3
"""
Test script to verify the improved sentence splitting works with file upload.
"""

import requests
import json

def test_file_upload():
    """Test uploading a file with formatting to verify sentence splitting."""
    
    print("🔧 TESTING FILE UPLOAD WITH IMPROVED SENTENCE SPLITTING")
    print("=" * 60)
    
    # Create test content with formatting
    test_content = """# Test Document

This is a sentence with **bold text** in the middle and should not be split.

Here is a sentence with a [link](http://example.com) that should stay together.

First sentence ends here. Second sentence has **formatting** and continues.
"""
    
    # Write to a temporary file
    with open('temp_test.md', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Upload the file
        with open('temp_test.md', 'rb') as f:
            files = {'file': ('temp_test.md', f, 'text/markdown')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Upload successful!")
            print("\nSentences detected:")
            
            for i, sentence_data in enumerate(data.get('sentences', [])):
                sentence = sentence_data.get('sentence', '')
                print(f"{i+1}. {sentence}")
            
            print(f"\nTotal sentences: {len(data.get('sentences', []))}")
            
            # Check if sentences with formatting were preserved
            sentences = [s.get('sentence', '') for s in data.get('sentences', [])]
            
            # Expected sentences (approximately)
            print("\n🔍 Validation:")
            for sentence in sentences:
                if 'bold text' in sentence and 'middle' in sentence:
                    if sentence.count('.') == 1 and sentence.endswith('split.'):
                        print("✅ Bold text sentence preserved correctly")
                    else:
                        print("❌ Bold text sentence was split incorrectly")
                
                if 'link' in sentence and 'stay together' in sentence:
                    if sentence.count('.') == 1:
                        print("✅ Link sentence preserved correctly")
                    else:
                        print("❌ Link sentence was split incorrectly")
        
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Clean up
        import os
        if os.path.exists('temp_test.md'):
            os.remove('temp_test.md')

if __name__ == "__main__":
    test_file_upload()
