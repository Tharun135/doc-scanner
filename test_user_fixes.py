#!/usr/bin/env python3
"""
Test the AI suggestion endpoint with the specific example from the user
"""

import requests
import json

def test_ai_suggestion_with_user_example():
    """Test the AI suggestion with the user's specific example"""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    # User's example
    sentence = "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags."
    issue = "You select the corresponding option for chosen tags, which makes Modbus TCP tags available in the Databus."
    
    # Test data
    data = {
        "feedback": issue,
        "sentence": sentence,
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness", "active_voice"]
    }
    
    print("🧪 Testing AI Suggestion with User Example")
    print("=" * 60)
    print(f"Original sentence: {sentence}")
    print(f"Issue detected: {issue}")
    print(f"Requesting AI suggestion...")
    
    try:
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AI Suggestion Generated Successfully!")
            print(f"Suggestion: {result['suggestion']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Method: {result['method']}")
            print(f"Model Used: {result.get('context_used', {}).get('model_used', 'Unknown')}")
            
            # Check if it's an improved suggestion
            if "CORRECTED TEXT:" in result['suggestion']:
                print(f"\n✅ Suggestion contains corrected text as expected!")
            else:
                print(f"\n⚠️ Suggestion format might need adjustment")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error making request: {e}")

def test_long_sentence_detection():
    """Test that long sentences no longer include AI solutions in feedback"""
    
    url = "http://127.0.0.1:5000/analyze"
    
    # User's example - a long sentence
    test_text = "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags which happens to be very long."
    
    print("\n\n🧪 Testing Long Sentence Rule Changes")
    print("=" * 60)
    print(f"Test text: {test_text}")
    
    try:
        data = {"content": test_text}
        response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            
            # Check feedback for AI Solution presence
            has_ai_solution = False
            for feedback in result.get('feedback', []):
                if 'AI Solution:' in feedback.get('suggestion', ''):
                    has_ai_solution = True
                    print(f"❌ Found AI Solution in feedback: {feedback['suggestion']}")
                    break
            
            if not has_ai_solution:
                print(f"✅ No AI Solution found in feedback - rule fixed!")
                print(f"Sample feedback: {result.get('feedback', [])[:2]}")  # Show first 2 feedback items
            else:
                print(f"❌ AI Solution still present in feedback")
                
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing long sentence rule: {e}")

if __name__ == "__main__":
    test_ai_suggestion_with_user_example()
    test_long_sentence_detection()
