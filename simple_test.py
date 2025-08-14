#!/usr/bin/env python3

import requests
import time
import json

def simple_test():
    """Simple test to see if the fix worked"""
    
    print("🔍 SIMPLE TEST FOR SENTENCE ISSUES")
    print("=" * 50)
    
    # Wait for server
    print("⏳ Waiting for server...")
    time.sleep(3)
    
    # Very simple test content
    test_content = "The document was written by the author. This uses appropriate language."
    
    print(f"📝 Test content:")
    print(f"'{test_content}'")
    
    try:
        # Upload document
        print("\n📤 Uploading...")
        files = {'file': ('test.txt', test_content)}
        response = requests.post('http://localhost:5000/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            
            sentences = result.get('sentences', [])
            print(f"\n📝 Found {len(sentences)} sentences:")
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\nSentence {i}:")
                sentence_text = sentence.get('sentence', '')[:100]
                html_text = sentence.get('html_text', '')[:100]
                
                print(f"  Sentence: {sentence_text}")
                print(f"  HTML: {html_text}")
                
                issues = sentence.get('feedback', [])
                print(f"  Issues: {len(issues)}")
                for j, issue in enumerate(issues, 1):
                    issue_text = issue.get('text', '')
                    issue_msg = issue.get('message', '')
                    print(f"    {j}. '{issue_text}' -> {issue_msg}")
            
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_test()
