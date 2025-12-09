#!/usr/bin/env python3
"""
Quick test to verify upload endpoint is working
"""
import requests
import io

# Create a simple test file
test_content = "This is a test document. It has multiple sentences. Each sentence should be analyzed."

# Upload to the server
url = "http://localhost:5000/upload"

files = {
    'file': ('test.txt', io.BytesIO(test_content.encode()), 'text/plain')
}

data = {
    'room_id': 'test_room_123'
}

print("🧪 Testing upload endpoint...")
print(f"URL: {url}")
print(f"File: test.txt")
print(f"Content length: {len(test_content)} bytes")
print()

try:
    response = requests.post(url, files=files, data=data, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    print("Response Body:")
    print(response.text[:500])  # First 500 chars
    
    if response.status_code == 200:
        print("\n✅ Upload endpoint is working!")
    else:
        print(f"\n❌ Upload failed with status {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - server may be hanging")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
