import requests
import sys
import os

def test_zip_upload():
    """Test ZIP file upload functionality"""
    
    test_file = "test_documents.zip"
    if not os.path.exists(test_file):
        print("❌ Test ZIP file not found:", test_file)
        return False
    
    # Server URL
    url = "http://127.0.0.1:5000/upload"
    
    try:
        # Prepare the file upload
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'room_id': 'test-zip-123'}
            
            print(f"🔄 Testing ZIP file upload...")
            response = requests.post(url, files=files, data=data)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ ZIP upload successful!")
                print(f"📊 Found {len(result.get('sentences', []))} sentences")
                
                # Show first few sentences to verify content
                sentences = result.get('sentences', [])
                for i, sentence_data in enumerate(sentences[:5]):
                    sentence_text = sentence_data.get('sentence', '')
                    print(f"📝 Sentence {i}: {sentence_text[:80]}...")
                
                print(f"📋 Quality score: {result.get('report', {}).get('avgQualityScore', 'N/A')}")
                return True
            else:
                print("❌ ZIP upload failed!")
                try:
                    error_data = response.json()
                    print(f"🔍 Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"🔍 HTTP Error: {response.status_code} - {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_zip_upload()
    sys.exit(0 if success else 1)