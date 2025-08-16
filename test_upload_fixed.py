"""
Test the upload with the fixed response format
"""

import requests
import json

def test_upload_with_fixed_format():
    url = "http://127.0.0.1:5000/upload"
    
    # Create test content
    test_content = "microsoft should be capitalized. This are wrong grammar."
    
    # Prepare the file data
    files = {
        'file': ('test.txt', test_content, 'text/plain')
    }
    
    try:
        print("🧪 Testing upload endpoint with fixed format...")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"📊 Found {len(data.get('sentences', []))} sentences")
            
            # Check the format of the first sentence
            if data.get('sentences'):
                first_sentence = data['sentences'][0]
                print("\n🔍 First sentence structure:")
                for key, value in first_sentence.items():
                    if key == 'feedback':
                        print(f"  {key}: {len(value)} issues")
                        for i, issue in enumerate(value):
                            print(f"    Issue {i+1}: {issue}")
                    else:
                        print(f"  {key}: {str(value)[:100]}...")
                
                # Check if the required properties exist
                required_props = ['sentence', 'html_segment', 'feedback', 'content', 'plain']
                missing_props = [prop for prop in required_props if prop not in first_sentence]
                
                if missing_props:
                    print(f"❌ Missing properties: {missing_props}")
                else:
                    print("✅ All required properties present!")
                    
            return True
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_upload_with_fixed_format()
