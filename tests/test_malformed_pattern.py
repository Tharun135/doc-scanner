import requests
import sys
import os

def test_malformed_html_pattern():
    """Test the specific malformed HTML pattern you're seeing"""
    
    # Create a test file with the exact problematic pattern
    test_content = '''="sentence-highlight" id="content-sentence-0" data-sentence-index="0">Parameters in application settings of PROFINET IO Connector should be configured properly.

This document contains the exact malformed pattern that is causing issues.

Another sentence with normal content for comparison.'''
    
    test_file = "test_malformed_pattern.txt"
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Server URL
    url = "http://127.0.0.1:5000/upload"
    
    try:
        # Prepare the file upload
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'room_id': 'test-malformed-123'}
            
            print(f"🔄 Testing upload with malformed HTML pattern...")
            print(f"📄 Content preview: {test_content[:100]}...")
            
            response = requests.post(url, files=files, data=data)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📊 Found {len(result.get('sentences', []))} sentences")
                
                # Check if the malformed pattern was cleaned
                sentences = result.get('sentences', [])
                for i, sentence_data in enumerate(sentences):
                    sentence_text = sentence_data.get('sentence', '')
                    print(f"📝 Sentence {i}: {sentence_text}")
                    
                    if '="' in sentence_text:
                        print(f"❌ Sentence {i} still contains malformed pattern!")
                    elif 'Parameters in application settings' in sentence_text:
                        print(f"✅ Target sentence cleaned successfully!")
                
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
    success = test_malformed_html_pattern()
    sys.exit(0 if success else 1)