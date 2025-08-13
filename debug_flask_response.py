#!/usr/bin/env python3
"""Debug the actual HTTP response from the Flask server"""

import requests
import io
import json

# Test content
test_content = """The document was written. It was reviewed by the team."""

print("Debugging Flask HTTP response...")
print("=" * 60)

url = "http://127.0.0.1:5000/upload"

# Create a file-like object
file_content = test_content.encode('utf-8')
files = {
    'file': ('test_document.txt', io.BytesIO(file_content), 'text/plain')
}

try:
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nFull JSON Response:")
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Error Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
