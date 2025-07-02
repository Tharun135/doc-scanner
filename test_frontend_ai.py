#!/usr/bin/env python3
"""
Test the exact AI suggestion request that the frontend makes
"""

import requests
import json

def test_ai_suggestion_endpoint():
    """Test the AI suggestion endpoint with the exact same request the frontend makes"""
    
    # Test with your example sentence
    test_data = {
        "feedback": "Long sentence detected (29 words). Consider breaking this into shorter sentences for better readability.",
        "sentence": "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"]
    }
    
    try:
        print("🧪 Testing AI suggestion endpoint...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            'http://127.0.0.1:5000/ai_suggestion',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_different_feedback_formats():
    """Test with different feedback formats to see which ones work"""
    
    test_cases = [
        {
            "name": "Clean feedback",
            "feedback": "Long sentence detected",
            "sentence": "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags."
        },
        {
            "name": "Issue prefix format",
            "feedback": "Issue: Long sentence detected (29 words)",
            "sentence": "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags."
        },
        {
            "name": "Complex feedback",
            "feedback": "Issue: Long sentence detected (29 words). Consider breaking this into shorter sentences for better readability.\nOriginal sentence: \"Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags.\"",
            "sentence": "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags."
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        test_data = {
            "feedback": test_case["feedback"],
            "sentence": test_case["sentence"],
            "document_type": "technical",
            "writing_goals": ["clarity", "conciseness"]
        }
        
        try:
            response = requests.post(
                'http://127.0.0.1:5000/ai_suggestion',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['suggestion'][:100]}...")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 AI Suggestion Endpoint Testing")
    print("=" * 50)
    
    print("\n1. Testing main endpoint...")
    success = test_ai_suggestion_endpoint()
    
    print("\n2. Testing different feedback formats...")
    test_different_feedback_formats()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Basic test passed - issue may be in frontend logic")
    else:
        print("❌ Backend endpoint has issues")
