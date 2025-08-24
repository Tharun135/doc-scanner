#!/usr/bin/env python3
"""
Test specific passive voice rewrite patterns.
"""

import requests

def test_rewrite_patterns():
    """Test the new rewrite pattern extraction."""
    
    print("🔍 TESTING REWRITE PATTERN EXTRACTION")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Clear Passive Voice",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was uploaded by the user."
        },
        {
            "name": "System Configuration",
            "feedback": "passive voice detected by rule", 
            "sentence": "The system can be configured by administrators."
        },
        {
            "name": "Report Generation",
            "feedback": "passive voice detected by rule",
            "sentence": "The report was generated automatically."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*50}")
        
        print(f"📝 Input:")
        print(f"   Feedback: '{test_case['feedback']}'")
        print(f"   Sentence: '{test_case['sentence']}'")
        
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
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                
                print(f"\n✅ Response:")
                print(f"   Method: {method}")
                print(f"   AI Answer: \"{ai_answer}\"")
                print(f"   Suggestion: \"{suggestion}\"")
                
                # Analysis
                print(f"\n📊 ANALYSIS:")
                
                # Check for patterns in AI response
                patterns_found = []
                if "rewrite:" in ai_answer.lower():
                    patterns_found.append("rewrite:")
                if "use active voice:" in ai_answer.lower():
                    patterns_found.append("use active voice:")
                if '"' in ai_answer:
                    patterns_found.append("quoted text")
                
                print(f"   Patterns in AI response: {patterns_found}")
                
                # Check if suggestion is different from original
                if suggestion != test_case['sentence']:
                    print(f"   ✅ Suggestion differs from original")
                    
                    # Check if it's a proper active voice conversion
                    original_lower = test_case['sentence'].lower()
                    suggestion_lower = suggestion.lower()
                    
                    if 'was' in original_lower and 'was' not in suggestion_lower:
                        print(f"   ✅ Successfully removed 'was' from passive voice")
                    elif 'can be' in original_lower and 'can' in suggestion_lower:
                        print(f"   ✅ Successfully converted 'can be' construction")
                else:
                    print(f"   ❌ Suggestion identical to original")
                
                # Check for common active voice indicators
                active_indicators = ['user uploads', 'administrators configure', 'system generates']
                suggestion_words = suggestion.lower()
                found_active = any(indicator in suggestion_words for indicator in active_indicators)
                if found_active:
                    print(f"   ✅ Contains active voice construction")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rewrite_patterns()
    
    print(f"\n💡 SUCCESS CRITERIA:")
    print(f"✅ AI Answer contains 'Rewrite:' pattern")
    print(f"✅ Suggestion extracts content after 'Rewrite:'") 
    print(f"✅ Suggestion converts passive to active voice")
    print(f"✅ No truncation with '...'")
    print(f"✅ Method shows 'ollama_rag_direct'")
