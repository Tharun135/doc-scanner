#!/usr/bin/env python3
"""
Test the improved backup/back up handling through the AI endpoint.
"""

import requests
import json

def test_backup_endpoint():
    """Test the backup improvements through the HTTP endpoint."""
    print("🧪 TESTING IMPROVED BACKUP/BACK UP THROUGH AI ENDPOINT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Original problematic case - should NOT change",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "Both options support backup files from the"
        },
        {
            "name": "Incorrect verb usage - should change",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "Remember to backup your data regularly"
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
                    original = test_case['sentence']
                    if corrected_text == original and "backup files" in original:
                        print(f"   ✅ CORRECT: Properly preserved noun usage 'backup files'")
                    elif "back up" in corrected_text and "backup" in original and "your" in original:
                        print(f"   ✅ CORRECT: Properly converted verb usage to 'back up'")
                    elif corrected_text != original:
                        print(f"   ⚠️  CHANGED: {original} → {corrected_text}")
                    else:
                        print(f"   📝 No change made")
                else:
                    print(f"   ⚠️  No structured correction found")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_backup_endpoint()
