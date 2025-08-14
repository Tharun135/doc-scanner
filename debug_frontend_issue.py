#!/usr/bin/env python3
"""
Simple test to check browser console for JavaScript errors
"""

import requests
import json
import time

def create_test_page():
    """Create a simple test page that logs everything"""
    
    test_content = """The document was written by the author. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point."""
    
    print("🔍 Testing with simple upload...")
    
    url = "http://localhost:5000/upload"
    files = {'file': ('test.txt', test_content.encode('utf-8'), 'text/plain')}
    
    try:
        response = requests.post(url, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Upload successful!")
            print(f"Number of sentences: {len(result.get('sentences', []))}")
            
            # Check each sentence for issues
            sentences = result.get('sentences', [])
            for i, sentence in enumerate(sentences):
                feedback = sentence.get('feedback', [])
                print(f"\nSentence {i+1}: '{sentence.get('sentence', '')[:50]}...'")
                print(f"  Issues: {len(feedback)}")
                
                for j, issue in enumerate(feedback):
                    print(f"    {j+1}. {issue.get('message', 'No message')}")
            
            # Save result for debugging
            with open('debug_upload_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n📁 Result saved to debug_upload_result.json")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_page()
