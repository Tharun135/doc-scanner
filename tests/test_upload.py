"""
Test Upload Functionality - Debug upload errors
"""

import requests
import os

def test_upload_functionality():
    """Test the upload endpoint to identify issues."""
    print("🧪 TESTING UPLOAD FUNCTIONALITY")
    print("=" * 50)
    
    # Test if Flask app is running
    try:
        response = requests.get("http://127.0.0.1:5000")
        print(f"✅ Flask app is running: {response.status_code}")
    except Exception as e:
        print(f"❌ Flask app not accessible: {e}")
        return
    
    # Test upload endpoint with a simple text file
    try:
        # Create a test file
        test_content = "This is a test document. It has multiple sentences. Let's see if the upload works correctly."
        test_file_path = "test_upload.txt"
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        print(f"\n📤 Testing upload with test file...")
        
        # Upload the file
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            response = requests.post("http://127.0.0.1:5000/upload", files=files)
        
        print(f"Upload response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            result = response.json()
            print(f"   Sentences analyzed: {len(result.get('sentences', []))}")
            print(f"   Total words: {result.get('report', {}).get('totalWords', 'unknown')}")
        else:
            print(f"❌ Upload failed!")
            print(f"   Error response: {response.text}")
        
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        
        # Clean up on error
        test_file_path = "test_upload.txt"
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_upload_functionality()
