#!/usr/bin/env python3
"""
Test the improved modal verb handling through the complete AI suggestion endpoint.
"""

import requests
import json

def test_modal_verb_endpoint():
    """Test the modal verb improvements through the HTTP endpoint."""
    print("🧪 TESTING IMPROVED MODAL VERB THROUGH AI ENDPOINT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Original problematic case",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "You can migrate an existing configuration from SIMATIC S7 Connector in two ways:"
        },
        {
            "name": "Users can access case",
            "feedback": "Use of modal verb 'can' - should describe direct action", 
            "sentence": "Users can access their data through the dashboard."
        },
        {
            "name": "System can process case",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "The system can process multiple requests simultaneously."
        }
    ]
    
    ai_url = "http://127.0.0.1:5000/ai_suggestion"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Original: {test_case['sentence']}")
        
        test_data = {
            "feedback": test_case['feedback'],
            "sentence": test_case['sentence'],
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"]
        }
        
        try:
            response = requests.post(ai_url, json=test_data, timeout=30)
            
            if response.ok:
                result = response.json()
                suggestion = result.get('suggestion', '')
                confidence = result.get('confidence', '')
                method = result.get('method', '')
                
                print(f"✅ AI Response received:")
                print(f"   Method: {method}")
                print(f"   Confidence: {confidence}")
                print(f"   Suggestion: {suggestion}")
                
                # Check if suggestion contains corrected text
                if "CORRECTED TEXT:" in suggestion:
                    lines = suggestion.split('\n')
                    corrected_line = [line for line in lines if line.startswith("CORRECTED TEXT:")][0]
                    corrected_text = corrected_line.replace("CORRECTED TEXT:", "").strip().strip('"')
                    print(f"   ✨ Corrected: {corrected_text}")
                    
                    # Validate the correction
                    if "You migrate" in corrected_text:
                        print(f"   ❌ Grammar issue: 'You migrate' is still incorrect")
                    elif corrected_text != test_case['sentence']:
                        print(f"   ✅ Proper improvement made!")
                    else:
                        print(f"   ⚠️  No change detected")
                else:
                    print(f"   ⚠️  No structured correction found")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_modal_verb_endpoint()
