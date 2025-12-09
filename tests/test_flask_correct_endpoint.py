#!/usr/bin/env python3
"""
Test the correct Flask AI endpoint with capitalization
"""
import requests
import json

def test_flask_ai_endpoint():
    """Test the Flask /ai_suggestion endpoint with capitalization issue"""
    
    # Test case: Capitalization issue
    data = {
        'feedback': 'Start sentences with a capital letter.',
        'sentence': 'it is in ISO 8601 Zulu format.',
        'document_type': 'general'
    }
    
    print(f"🔍 Testing Flask /ai_suggestion endpoint:")
    print(f"  Sentence: '{data['sentence']}'")
    print(f"  Feedback: '{data['feedback']}'")
    
    try:
        response = requests.post('http://localhost:5000/ai_suggestion', json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Status: {response.status_code}")
            print(f"  Method: {result.get('method', 'Unknown')}")
            print(f"  Suggestion: '{result.get('suggestion', '')}'")
            print(f"  AI Answer: '{result.get('ai_answer', '')}'")
            print(f"  Confidence: {result.get('confidence', 'Unknown')}")
            
            # Check if capitalization is fixed
            suggestion = result.get('suggestion', '')
            if suggestion:
                is_capitalized = suggestion[0].isupper()
                no_improved_prefix = not suggestion.startswith("Improved:")
                print(f"  ✅ Capitalized: {is_capitalized}")
                print(f"  ✅ No 'Improved:' prefix: {no_improved_prefix}")
            else:
                print(f"  ❌ Empty suggestion")
        else:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("  ❌ Flask server not running at http://localhost:5000")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_flask_ai_endpoint()
