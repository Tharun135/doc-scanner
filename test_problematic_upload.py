import requests
import sys
import os

def test_upload_problematic():
    """Test file upload with problematic HTML content"""
    
    # Test file path - rename to .txt so it gets processed correctly
    test_file = "test_problematic.txt"
    
    # Copy the HTML content to a txt file for testing
    with open("test_problematic.html", 'r') as html_file:
        content = html_file.read()
    
    with open(test_file, 'w') as txt_file:
        txt_file.write(content)
    
    if not os.path.exists(test_file):
        print("❌ Test file not found:", test_file)
        return False
    
    # Server URL
    url = "http://127.0.0.1:5000/upload"
    
    try:
        # Prepare the file upload
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'room_id': 'test-problematic-123'}
            
            print(f"🔄 Testing upload of {test_file} (contains problematic HTML)...")
            response = requests.post(url, files=files, data=data)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📊 Found {len(result.get('sentences', []))} sentences")
                
                # Check if any sentences contain HTML markup
                sentences = result.get('sentences', [])
                for i, sentence_data in enumerate(sentences):
                    sentence_text = sentence_data.get('sentence', '')
                    if '<' in sentence_text and '>' in sentence_text:
                        print(f"⚠️ Sentence {i} still contains HTML: {sentence_text}")
                    else:
                        print(f"✅ Sentence {i} is clean: {sentence_text[:50]}...")
                
                return True
            else:
                print("❌ Upload failed!")
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
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    success = test_upload_problematic()
    sys.exit(0 if success else 1)