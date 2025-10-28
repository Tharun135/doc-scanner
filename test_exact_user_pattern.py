import requests
import sys
import os

def test_exact_user_pattern():
    """Test with the exact pattern the user is seeing"""
    
    # Create a document that might trigger this specific pattern
    test_content = """="sentence-highlight" id="content-sentence-0" data-sentence-index="0">Parameters in application settings of PROFINET IO Connector

Some additional content here to make it a complete document.

This should help us understand where this malformed pattern comes from."""
    
    test_file = "test_exact_pattern.txt"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Server URL
    url = "http://127.0.0.1:5000/upload"
    
    try:
        # Prepare the file upload
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {'room_id': 'test-exact-pattern-123'}
            
            print(f"🔄 Testing upload with exact user pattern...")
            print(f"📄 Content: {test_content[:100]}...")
            
            response = requests.post(url, files=files, data=data)
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📊 Found {len(result.get('sentences', []))} sentences")
                
                # Check each sentence for the problematic pattern
                sentences = result.get('sentences', [])
                for i, sentence_data in enumerate(sentences):
                    sentence_text = sentence_data.get('sentence', '')
                    print(f"📝 Sentence {i}: '{sentence_text}'")
                    
                    # Check for the specific malformed pattern
                    if '="sentence-highlight"' in sentence_text:
                        print(f"🚨 FOUND MALFORMED PATTERN in sentence {i}!")
                        print(f"   Full text: {sentence_text}")
                        
                    if 'Parameters in application settings' in sentence_text:
                        print(f"✅ Target content found in sentence {i}")
                        if sentence_text.startswith('Parameters'):
                            print(f"✅ Sentence appears clean: {sentence_text}")
                        else:
                            print(f"⚠️ Sentence may have prefix: {sentence_text}")
                
                return len([s for s in sentences if '="sentence-highlight"' in s.get('sentence', '')]) == 0
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
    success = test_exact_user_pattern()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Malformed pattern {'not found' if success else 'still present'}")
    sys.exit(0 if success else 1)