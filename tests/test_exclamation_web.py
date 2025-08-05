#!/usr/bin/env python3
"""
Test the exclamation mark fix using the web upload functionality
"""

import requests

def test_exclamation_via_upload():
    """Test via web upload to see if the fix works."""
    
    test_cases = [
        {
            "name": "NOTE template (should NOT trigger)",
            "content": """
> **NOTE**! This is important information.

Regular content follows here. This is a normal sentence.
"""
        },
        {
            "name": "Excessive exclamation marks (should trigger)", 
            "content": """
This is amazing! It's so cool! I love this feature! 
Everything is awesome! This is the best! What a great tool!
"""
        }
    ]
    
    url = "http://127.0.0.1:5000/upload"
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"Content preview: {repr(test_case['content'][:50])}...")
        
        files = {
            'file': ('test.txt', test_case['content'], 'text/plain')
        }
        
        try:
            response = requests.post(url, files=files, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # Look for exclamation mark warnings
                exclamation_warnings = []
                for sentence in result.get('sentences', []):
                    for feedback in sentence.get('feedback', []):
                        message = feedback.get('message', '')
                        if 'exclamation marks' in message.lower():
                            exclamation_warnings.append(message)
                
                if exclamation_warnings:
                    print(f"   ⚠️ Found exclamation warnings:")
                    for warning in exclamation_warnings:
                        print(f"      • {warning}")
                else:
                    print(f"   ✅ No exclamation warnings found")
                
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Test completed!")

if __name__ == "__main__":
    test_exclamation_via_upload()
