#!/usr/bin/env python3
"""
Test the fix via actual web upload
"""

import requests

def test_note_template_upload():
    """Test uploading the NOTE template file."""
    
    url = "http://127.0.0.1:5000/upload"
    
    # Read the NOTE-only test file
    with open('test_note_only.md', 'r') as f:
        content = f.read()
    
    print("Testing NOTE template upload...")
    print("Content preview:")
    print(content[:200] + "...")
    print()
    
    files = {
        'file': ('test_note_only.md', content, 'text/markdown')
    }
    
    try:
        response = requests.post(url, files=files, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Upload successful!")
            print(f"Total sentences: {result.get('report', {}).get('totalSentences', 'N/A')}")
            
            # Look specifically for exclamation mark warnings
            exclamation_warnings = []
            total_feedback = 0
            
            for sentence in result.get('sentences', []):
                total_feedback += len(sentence.get('feedback', []))
                for feedback in sentence.get('feedback', []):
                    message = feedback.get('message', '')
                    if 'exclamation marks' in message.lower():
                        exclamation_warnings.append(message)
            
            print(f"Total feedback items: {total_feedback}")
            
            if exclamation_warnings:
                print(f"❌ Still found exclamation warnings:")
                for warning in exclamation_warnings:
                    print(f"   • {warning}")
                return False
            else:
                print(f"✅ No exclamation warnings found - fix is working!")
                return True
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_note_template_upload()
