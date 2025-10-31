#!/usr/bin/env python3
"""
Test the /ai_suggestion endpoint that the web interface actually uses
"""

import requests
import json

def test_ai_suggestion_endpoint():
    print("🧪 Testing /ai_suggestion Endpoint (Web Interface)")
    print("=" * 55)
    
    test_cases = [
        {
            "input": "A data source must be created.",
            "feedback": "Avoid passive voice in sentence",
            "expected": "You must create a data source."
        },
        {
            "input": "The available connectors are shown.",
            "feedback": "Avoid passive voice in sentence", 
            "expected": "The system shows the available connectors."
        },
        {
            "input": "The list of available tags is displayed.",
            "feedback": "Avoid passive voice in sentence",
            "expected": "The system displays the list of available tags."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{case['input']}'")
        print(f"📋 Feedback: '{case['feedback']}'")
        print(f"🎯 Expected: '{case['expected']}'")
        
        try:
            payload = {
                "sentence": case["input"],
                "feedback": case["feedback"],
                "issue_type": "Passive Voice",
                "document_type": "technical",
                "writing_goals": ["clarity", "directness"],
                "option_number": 1
            }
            
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json=payload,
                timeout=30
            )
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get('suggestion', '').strip()
                ai_answer = result.get('ai_answer', '').strip()
                method = result.get('method', 'N/A')
                
                print(f"💡 Suggestion: '{suggestion}'")
                print(f"🤖 AI Answer: '{ai_answer[:100]}{'...' if len(ai_answer) > 100 else ''}'")
                print(f"📊 Method: {method}")
                
                # Check for issues
                if suggestion.startswith('#') or '{' in suggestion[:50]:
                    print("❌ ISSUE: Got raw JSON/file content instead of conversion!")
                elif case['expected'] == suggestion:
                    print("✅ PERFECT MATCH!")
                elif suggestion != case['input']:
                    print("✅ CONVERTED (different than expected)")
                else:
                    print("❌ NO CONVERSION - returned original text")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:300]}...")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_ai_suggestion_endpoint()