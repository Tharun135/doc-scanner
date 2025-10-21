#!/usr/bin/env python3
"""
Test the AI suggestion endpoint directly to debug the response structure issue
"""

import requests
import json
import sys

def test_ai_suggestion_endpoint():
    """Test the AI suggestion endpoint with the problematic case"""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    # Test the exact case that was failing
    test_data = {
        "feedback": "Check use of adverb: 'only' in sentence 'In the IEM, you only get a very general overview about the CPU load of an app.'",
        "sentence": "In the IEM, you only get a very general overview about the CPU load of an app.",
        "documentType": "technical",
        "writingGoals": "clarity",
        "optionNumber": 1
    }
    
    print("🧪 Testing AI Suggestion Endpoint")
    print("="*50)
    print(f"📝 URL: {url}")
    print(f"📋 Test Data: {json.dumps(test_data, indent=2)}")
    print()
    
    try:
        # Send POST request
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            # Parse JSON response
            try:
                result = response.json()
                print("✅ JSON Response Parsed Successfully:")
                print(json.dumps(result, indent=2))
                print()
                
                # Validate frontend requirements
                print("🔍 Frontend Validation Check:")
                is_valid = (result and 
                           isinstance(result, dict) and 
                           result.get('suggestion') and
                           bool(result.get('suggestion', '').strip()))
                
                print(f"   • Result exists: {bool(result)}")
                print(f"   • Is dict: {isinstance(result, dict)}")
                print(f"   • Has suggestion: {'suggestion' in result}")
                print(f"   • Suggestion not empty: {bool(result.get('suggestion', '').strip())}")
                print(f"   • Overall valid: {is_valid}")
                
                if not is_valid:
                    print("\n❌ VALIDATION FAILED - This would cause 'invalid response structure' error")
                else:
                    print("\n✅ VALIDATION PASSED - Response structure is valid")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"Raw response: {response.text}")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response body: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Flask app is not running")
        print("   Start the Flask app with: python run.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    test_ai_suggestion_endpoint()