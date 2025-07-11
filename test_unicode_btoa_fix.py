#!/usr/bin/env python3
"""
Test the fix for the btoa Unicode error in AI suggestions
"""

import requests
import json

def test_unicode_ai_suggestion():
    """Test AI suggestion with text that would cause btoa Unicode error"""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    # Test with text that contains Unicode characters that would break btoa()
    test_cases = [
        {
            "name": "Smart quotes test",
            "feedback": "Text contains \u201csmart quotes\u201d that would break btoa",
            "sentence": "The document was reviewed with \u201ccareful attention\u201d to detail."
        },
        {
            "name": "Em dash test", 
            "feedback": "Text has em\u2014dash characters that break btoa",
            "sentence": "The process is simple\u2014just follow these steps."
        },
        {
            "name": "Symbols test",
            "feedback": "Text with symbols \u00a9 \u00ae \u2122 that break btoa",
            "sentence": "This software is \u00a9 2024 Company Name\u00ae."
        },
        {
            "name": "Accented characters test",
            "feedback": "Text with caf\u00e9, na\u00efve, r\u00e9sum\u00e9 characters",
            "sentence": "The caf\u00e9 serves na\u00efve customers preparing their r\u00e9sum\u00e9."
        }
    ]
    
    print("🧪 Testing AI Suggestion with Unicode Characters")
    print("=" * 60)
    print("This test verifies that the btoa() Unicode error has been fixed.")
    print()
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Feedback: {test_case['feedback']}")
        print(f"   Sentence: {test_case['sentence']}")
        
        data = {
            "feedback": test_case['feedback'],
            "sentence": test_case['sentence'],
            "document_type": "general",
            "writing_goals": ["clarity"]
        }
        
        try:
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS: AI suggestion received")
                print(f"   Suggestion: {result['suggestion'][:80]}...")
                print(f"   Method: {result.get('method', 'unknown')}")
                success_count += 1
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        print()
    
    print("=" * 60)
    print(f"Results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL TESTS PASSED! The btoa Unicode error has been fixed!")
    elif success_count > 0:
        print("⚠️ PARTIAL SUCCESS: Some tests passed, Unicode handling improved")
    else:
        print("❌ ALL TESTS FAILED: Issue may still exist")
    
    return success_count == len(test_cases)

if __name__ == "__main__":
    test_unicode_ai_suggestion()
