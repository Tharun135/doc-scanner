#!/usr/bin/env python3
"""
Test script to debug the AI suggestion endpoint
"""

import requests
import json

def test_ai_suggestion():
    """Test the AI suggestion endpoint directly"""
    
    # Test data that matches what the frontend sends
    test_data = {
        "feedback": "Avoid using ALL CAPS for emphasis. Use bold or italic formatting instead.",
        "sentence": "Some of the properties of alarm notifications are specifically implemented for the SIMATIC S7+ Connector.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"],
        "option_number": 1
    }
    
    print("🔧 Testing AI suggestion endpoint...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:5000/ai_suggestion",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response OK: {response.ok}")
        
        if response.ok:
            result = response.json()
            print(f"\n✅ Response JSON:")
            print(json.dumps(result, indent=2))
            
            # Validate the structure
            print(f"\n🔍 Validation:")
            print(f"  - Has 'suggestion' key: {'suggestion' in result}")
            print(f"  - Suggestion value: {result.get('suggestion', 'N/A')}")
            print(f"  - Suggestion type: {type(result.get('suggestion'))}")
            print(f"  - Suggestion length: {len(result.get('suggestion', ''))}")
            print(f"  - Suggestion truthy: {bool(result.get('suggestion'))}")
            print(f"  - Suggestion after trim: '{result.get('suggestion', '').strip()}'")
            print(f"  - Trimmed length: {len(result.get('suggestion', '').strip())}")
            
            # Frontend validation (same as in JavaScript)
            suggestion = result.get('suggestion')
            is_valid = (result and 
                       isinstance(result, dict) and 
                       suggestion and 
                       suggestion.strip())
            
            print(f"\n🎯 Frontend validation result: {is_valid}")
            
            if is_valid:
                print("✅ Response would pass frontend validation")
            else:
                print("❌ Response would FAIL frontend validation")
                
        else:
            print(f"❌ Error response:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_suggestion()
