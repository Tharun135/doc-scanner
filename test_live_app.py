#!/usr/bin/env python3
"""
Test the live application's AI endpoint for concise responses
"""

import requests
import json

def test_live_app():
    """Test the running application's AI endpoint"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Live Application AI Responses...\n")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Passive Voice",
            "feedback": "Passive voice detected",
            "sentence": "The document was written by the team"
        },
        {
            "name": "Modal Verb",
            "feedback": "Modal verb usage: 'may' for permission",
            "sentence": "You may use this feature when needed"
        },
        {
            "name": "Long Sentence",
            "feedback": "Sentence is too long",
            "sentence": "This is a very long sentence that contains multiple clauses and should be broken down into smaller parts for better readability and comprehension."
        }
    ]
    
    for test in test_cases:
        print(f"📝 Test: {test['name']}")
        print(f"Issue: {test['feedback']}")
        print(f"Sentence: '{test['sentence']}'")
        print("-" * 40)
        
        try:
            response = requests.post(f"{base_url}/ai_suggestion", json={
                "feedback": test['feedback'],
                "sentence": test['sentence'],
                "document_type": "general"
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Method: {data.get('method', 'unknown')}")
                print(f"Suggestion: {data.get('suggestion', 'No suggestion')}")
                if 'gemini_answer' in data and data['gemini_answer']:
                    print(f"Gemini Answer: {data['gemini_answer']}")
                print("✅ Using Gemini AI" if data.get('method') == 'gemini_rag' else "⚠️ Using fallback")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        print()

if __name__ == "__main__":
    test_live_app()
