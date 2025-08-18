#!/usr/bin/env python3
"""Test the AI suggestion endpoint directly."""

import requests
import json

def test_ai_endpoint():
    """Test the /ai_suggestion endpoint."""
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    test_cases = [
        {
            "feedback": "passive voice detected",
            "sentence": "The report was written by the team.",
            "document_type": "technical",
            "writing_goals": ["clarity", "conciseness"]
        },
        {
            "feedback": "sentence is too long",
            "sentence": "There are many issues that need to be addressed in this document that was created by the development team and should be reviewed carefully.",
            "document_type": "technical",
            "writing_goals": ["clarity", "conciseness"]
        }
    ]
    
    print("Testing AI Suggestion Endpoint...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: {test_case['sentence']}")
        print(f"Issue: {test_case['feedback']}")
        print("-" * 30)
        
        try:
            response = requests.post(url, json=test_case, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get('suggestion', 'No suggestion returned')
                method = result.get('method', 'unknown')
                confidence = result.get('confidence', 'unknown')
                
                print(f"✓ SUCCESS: {method} ({confidence} confidence)")
                print(f"Suggestion: {suggestion}")
                
                # Check if it's a meaningful rewrite
                if suggestion != test_case['sentence'] and not suggestion.startswith("Rewrite needed:"):
                    print("✓ Generated proper rewrite")
                else:
                    print("✗ Did not generate proper rewrite")
                    
            else:
                print(f"✗ FAILED: HTTP {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"✗ ERROR: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_ai_endpoint()
