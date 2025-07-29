#!/usr/bin/env python3
"""
Simple test for the AI suggestion endpoint
"""

import requests
import json

def test_ai_endpoint():
    """Test the AI suggestion endpoint directly"""
    
    print("🧪 Testing AI Suggestion Endpoint")
    print("=" * 40)
    
    # Test data
    test_data = {
        "feedback": "This sentence contains passive voice",
        "sentence": "The document was created by the team.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"]
    }
    
    try:
        print(f"📤 Sending request to http://localhost:5000/ai_suggestion")
        print(f"📋 Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response structure:")
            print(f"   - suggestion: {bool(result.get('suggestion'))}")
            print(f"   - confidence: {result.get('confidence')}")
            print(f"   - method: {result.get('method')}")
            print(f"   - suggestion_id: {bool(result.get('suggestion_id'))}")
            
            if result.get('suggestion'):
                print(f"💬 Suggestion preview: {result['suggestion'][:100]}...")
                return True
            else:
                print(f"❌ No suggestion in response")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on localhost:5000?")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_ai_endpoint()
