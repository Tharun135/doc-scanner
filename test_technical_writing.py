#!/usr/bin/env python3
"""
Test technical writing focused responses
"""

import requests
import json

def test_technical_writing():
    """Test technical writing focused AI responses"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Technical Writing AI Responses...\n")
    print("=" * 60)
    
    # Test cases specifically for technical writing issues
    test_cases = [
        {
            "name": "Passive Voice with 'We'",
            "feedback": "Passive voice detected",
            "sentence": "The system was designed by us to handle multiple users"
        },
        {
            "name": "First Person Usage",
            "feedback": "Avoid first person in technical writing",
            "sentence": "We recommend that you backup your files regularly"
        },
        {
            "name": "Subjective Language",
            "feedback": "Too subjective for technical documentation",
            "sentence": "We believe this feature is very useful for most users"
        },
        {
            "name": "User Manual Instruction",
            "feedback": "Modal verb usage: 'may' for permission",
            "sentence": "You may save the file when you are ready"
        }
    ]
    
    for test in test_cases:
        print(f"📝 Test: {test['name']}")
        print(f"Issue: {test['feedback']}")
        print(f"Original: '{test['sentence']}'")
        print("-" * 50)
        
        try:
            response = requests.post(f"{base_url}/ai_suggestion", json={
                "feedback": test['feedback'],
                "sentence": test['sentence'],
                "document_type": "technical"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Method: {data.get('method', 'unknown')}")
                print(f"AI Suggestion: {data.get('suggestion', 'No suggestion')}")
                
                # Check if the suggestion contains "we" or other subjective language
                suggestion_text = data.get('suggestion', '').lower()
                if 'we ' in suggestion_text or ' us ' in suggestion_text or ' our ' in suggestion_text:
                    print("⚠️  WARNING: Suggestion still contains first-person pronouns!")
                else:
                    print("✅ Good: No first-person pronouns detected")
                    
                print("✅ Using Gemini AI" if data.get('method') == 'gemini_rag' else "⚠️ Using fallback")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        print()

if __name__ == "__main__":
    test_technical_writing()
