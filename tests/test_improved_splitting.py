#!/usr/bin/env python3
"""
Test the improved ollama_rag_direct with proper sentence splitting.
"""

import requests
import json

def test_long_sentence_splitting():
    """Test ollama_rag_direct with long sentence that should be split."""
    
    print("🔍 TESTING IMPROVED LONG SENTENCE SPLITTING")
    print("=" * 45)
    
    # Test the exact scenario from the user's example
    test_data = {
        'feedback': 'Consider breaking this long sentence into shorter ones',
        'sentence': "The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem."
    }
    
    print(f"📝 Testing long sentence splitting:")
    print(f"   Feedback: '{test_data['feedback']}'")
    print(f"   Original: '{test_data['sentence']}'")
    print(f"   Length: {len(test_data['sentence'])} characters")
    
    try:
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=35  # Allow extra time for processing
        )
        
        if response.status_code == 200:
            result = response.json()
            
            method = result.get('method', 'unknown')
            ai_answer = result.get('ai_answer', '')
            suggestion = result.get('suggestion', '')
            sources = result.get('sources', [])
            
            print(f"\n✅ Response received:")
            print(f"   Method: {method}")
            print(f"   AI Answer Length: {len(ai_answer)} chars")
            print(f"   Suggestion Length: {len(suggestion)} chars")
            print(f"   Sources: {len(sources)}")
            
            if method == 'ollama_rag_direct':
                print(f"\n🎯 ollama_rag_direct SUCCESS!")
                
                print(f"\n📋 AI Guidance:")
                print(f"   \"{ai_answer}\"")
                
                print(f"\n✏️ AI Suggestion (Expected: Split sentences):")
                print(f"   \"{suggestion}\"")
                
                print(f"\n📚 Knowledge Sources:")
                for i, source in enumerate(sources):
                    if isinstance(source, dict):
                        rule_id = source.get('rule_id', 'unknown')
                        title = source.get('title', 'unknown')
                        similarity = source.get('similarity', 0)
                        print(f"   {i+1}. Rule ID: {rule_id}")
                        print(f"      Title: {title}")
                        print(f"      Similarity: {similarity}")
                    else:
                        print(f"   {i+1}. {source}")
                
                # Check if the suggestion contains split sentences
                if '.' in suggestion and len(suggestion.split('.')) > 2:
                    print(f"\n✅ SUCCESS: Suggestion contains multiple sentences!")
                    sentences = [s.strip() for s in suggestion.split('.') if s.strip()]
                    for i, sent in enumerate(sentences, 1):
                        print(f"   Sentence {i}: \"{sent}.\"")
                else:
                    print(f"\n⚠️ ISSUE: Suggestion doesn't appear to contain split sentences")
                    print(f"   This might be truncated or need further optimization")
                    
            else:
                print(f"\n📚 Using fallback method: {method}")
                print(f"   AI Answer: \"{ai_answer[:100]}...\"")
                print(f"   Suggestion: \"{suggestion[:100]}...\"")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_other_scenarios():
    """Test a few other scenarios to ensure we didn't break anything."""
    
    print(f"\n🔄 TESTING OTHER SCENARIOS")
    print("=" * 30)
    
    test_cases = [
        {
            "name": "Passive Voice",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was saved by the user."
        },
        {
            "name": "Short Sentence", 
            "feedback": "improve clarity",
            "sentence": "Fix this."
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                method = result.get('method', 'unknown')
                print(f"   Method: {method} ✅")
            else:
                print(f"   HTTP Error: {response.status_code} ❌")
                
        except Exception as e:
            print(f"   Error: {e} ❌")

if __name__ == "__main__":
    test_long_sentence_splitting()
    test_other_scenarios()
    
    print(f"\n💡 EXPECTED IMPROVEMENTS:")
    print(f"1. AI Suggestion should contain actual split sentences")
    print(f"2. Knowledge Sources should show proper rule information")
    print(f"3. ollama_rag_direct should provide both guidance AND rewritten text")
    print(f"4. The suggestion should NOT be truncated")
