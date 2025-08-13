#!/usr/bin/env python3
"""Test exactly what the user might be seeing"""

import requests
import io
import json

def test_flask_endpoint(content, description):
    print(f"\n=== TESTING: {description} ===")
    print(f"Content: {repr(content)}")
    
    url = "http://127.0.0.1:5000/upload"
    
    # Create a file-like object
    file_content = content.encode('utf-8')
    files = {
        'file': ('test_document.txt', io.BytesIO(file_content), 'text/plain')
    }
    
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            total_issues = 0
            for sentence in result.get('sentences', []):
                issues = sentence.get('feedback', [])
                total_issues += len(issues)
                if issues:
                    print(f"Sentence: '{sentence.get('sentence', '')[:50]}...'")
                    for issue in issues:
                        print(f"  - {issue.get('message', 'No message')}")
            
            print(f"TOTAL ISSUES: {total_issues}")
            return total_issues
            
        else:
            print(f"ERROR: {response.status_code} - {response.text}")
            return 0
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 0

# Test various scenarios
print("🔍 DEBUGGING WEB INTERFACE ISSUE DETECTION")
print("=" * 60)

# Test 1: Simple passive voice
test_flask_endpoint("The document was written.", "Simple passive voice")

# Test 2: Verbose language
test_flask_endpoint("In order to utilize the system, you should make use of the interface.", "Verbose language")

# Test 3: Long sentence
test_flask_endpoint("This is a very long sentence that contains many words and clauses and should be detected as being too long for good readability and user experience.", "Long sentence")

# Test 4: Empty content
test_flask_endpoint("", "Empty content")

# Test 5: Single word
test_flask_endpoint("Hello", "Single word")

# Test 6: What user might actually be testing
test_flask_endpoint("Hello world. This is a test.", "Simple test content")

print(f"\n{'='*60}")
print("If all tests show 0 issues, there may be an issue with:")
print("1. Rule loading in the web interface")
print("2. Content processing in the upload route")
print("3. Response formatting")
print("4. Browser cache or interface display")
