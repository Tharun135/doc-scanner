#!/usr/bin/env python3
"""Test the improved issue-focused AI endpoint."""

import requests
import json

def test_improved_ai_endpoint():
    """Test the /ai_suggestion endpoint with issue-focused requests."""
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    test_cases = [
        {
            "feedback": "passive voice detected",
            "sentence": "The report was written by the team.",
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"],
            "expected_issue": "passive voice"
        },
        {
            "feedback": "sentence is too long and complex",
            "sentence": "There are many complex issues that need to be carefully addressed in this comprehensive document that was created by our experienced development team and should definitely be reviewed thoroughly by all stakeholders.",
            "document_type": "technical",
            "writing_goals": ["clarity", "conciseness"],
            "expected_issue": "long sentence"
        },
        {
            "feedback": "weak modal verb usage detected",
            "sentence": "The system can be used to process documents effectively.",
            "document_type": "technical",
            "writing_goals": ["directness", "clarity"],
            "expected_issue": "modal verbs"
        }
    ]
    
    print("Testing Improved Issue-Focused AI Endpoint...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['expected_issue'].upper()}")
        print(f"Original: {test_case['sentence']}")
        print(f"Issue: {test_case['feedback']}")
        print("-" * 40)
        
        try:
            response = requests.post(url, json=test_case, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get('suggestion', 'No suggestion returned')
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 'unknown')
                sources = result.get('sources', '')
                
                print(f"✓ METHOD: {method} ({confidence} confidence)")
                print(f"✓ SUGGESTION: {suggestion}")
                
                # Check if it's a meaningful solution to the specific issue
                if suggestion != test_case['sentence']:
                    if test_case['expected_issue'] == "passive voice":
                        if " by " not in suggestion or "team wrote" in suggestion.lower():
                            print("✅ SUCCESS: Addressed passive voice issue")
                        else:
                            print("🔄 PARTIAL: Generated different text but may not fully address passive voice")
                    elif test_case['expected_issue'] == "long sentence":
                        if len(suggestion.split()) < len(test_case['sentence'].split()) or "." in suggestion[:-1]:
                            print("✅ SUCCESS: Addressed long sentence issue")
                        else:
                            print("🔄 PARTIAL: Generated different text but may not be shorter")
                    elif test_case['expected_issue'] == "modal verbs":
                        if "can be" not in suggestion.lower():
                            print("✅ SUCCESS: Addressed modal verb issue")
                        else:
                            print("🔄 PARTIAL: Generated different text but may still have modal verbs")
                else:
                    print("❌ FAILED: Returned identical text")
                    
                if sources:
                    print(f"📚 KNOWLEDGE USED: {sources[:100]}...")
                    
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_improved_ai_endpoint()
