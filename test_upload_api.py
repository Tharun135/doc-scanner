#!/usr/bin/env python3
"""
Test the upload functionality by making a direct API call to the running Flask app.
"""

import requests
import io
import os
import time

def test_upload_to_running_app():
    """Test uploading a document to the Flask app."""
    print("🧪 Testing Document Upload to Running Flask App")
    print("=" * 50)
    
    # Flask app should be running on localhost:5000
    base_url = "http://localhost:5000"
    
    # Test 1: Check if app is responding
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Flask app is responding: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        return False
    
    # Test 2: Test document upload
    try:
        # Create a test document
        test_content = """
        This is a test document for upload testing.
        
        It contains some vague terms like very good performance and excellent results.
        This sentence is quite long and might be flagged by the long sentence detector because it contains many words and clauses that could potentially be split into shorter, more digestible sentences.
        
        The document should be processed successfully without any spaCy E088 errors.
        """
        
        # Create file-like object
        file_data = io.BytesIO(test_content.encode('utf-8'))
        file_data.name = 'test_upload.txt'
        
        # Upload the file - reset file pointer  
        file_data.seek(0)
        files = {'files[]': ('test_upload.txt', file_data, 'text/plain')}
        
        print("📤 Uploading test document...")
        response = requests.post(f"{base_url}/rag/upload_knowledge", files=files, timeout=30)
        
        print(f"📊 Upload response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

if __name__ == "__main__":
    # Wait a moment for Flask to be fully ready
    print("⏳ Waiting 3 seconds for Flask to be fully ready...")
    time.sleep(3)
    
    success = test_upload_to_running_app()
    if success:
        print(f"\n🎉 UPLOAD TEST PASSED!")
        print(f"✅ Document upload functionality is working!")
        print(f"✅ The '0 docs' issue should be resolved!")
    else:
        print(f"\n❌ Upload test failed - needs investigation")