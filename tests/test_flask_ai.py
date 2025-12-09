#!/usr/bin/env python3
"""
Test the Flask AI suggestion endpoint with exact frontend parameters
"""

import requests
import json
import time

def test_flask_ai_suggestion():
    """Test the Flask endpoint with frontend parameters"""
    print("🔧 Testing Flask AI suggestion endpoint...")
    
    # This matches exactly what the frontend sends
    request_data = {
        "feedback": "Avoid using ALL CAPS for emphasis. Use bold or italic formatting instead.",
        "sentence": "Some of the properties of alarm notifications are specifically implemented for the SIMATIC S7+ Connector.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"],
        "option_number": 1
    }
    
    print("\nRequest data:")
    print(json.dumps(request_data, indent=2))
    
    try:
        # Try to connect to the server
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n✅ HTTP request successful!")
        print(f"📝 Response status: {response.status_code}")
        print(f"📝 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n✅ JSON parse successful!")
                print(f"📝 Result type: {type(result)}")
                print(f"📝 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                if isinstance(result, dict):
                    print(f"\n🔍 Analyzing response structure:")
                    for key, value in result.items():
                        print(f"   - {key}: {type(value)} = {repr(value)[:100]}...")
                    
                    # Test JavaScript validation logic
                    if result.get('suggestion'):
                        suggestion = result['suggestion']
                        if hasattr(suggestion, 'strip') and suggestion.strip():
                            print(f"\n✅ Would pass JavaScript validation: result.suggestion && result.suggestion.trim()")
                        else:
                            print(f"\n❌ Would fail JavaScript validation: suggestion = {repr(suggestion)}")
                    else:
                        print(f"\n❌ Would fail JavaScript validation: no suggestion key or falsy suggestion")
                else:
                    print(f"\n❌ Response is not a JSON object: {result}")
                
                return result
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON parse failed: {e}")
                print(f"Response text: {response.text}")
                return None
        else:
            print(f"\n❌ HTTP error: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection failed - server not running on localhost:5000")
        print("💡 Start server with: python run.py")
        return None
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        return None

if __name__ == "__main__":
    test_flask_ai_suggestion()