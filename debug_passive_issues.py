#!/usr/bin/env python3
"""
Debug the passive voice issues with truncated suggestions and undefined sources.
"""

import requests
import json

def test_passive_voice_issues():
    """Test the specific passive voice cases that are problematic."""
    
    print("🔍 DEBUGGING PASSIVE VOICE ISSUES")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Requirement Statement",
            "feedback": "Avoid passive voice in sentence: 'The following requirement must be met:'",
            "sentence": "The following requirement must be met:"
        },
        {
            "name": "IED Access Fragment", 
            "feedback": "Avoid passive voice in sentence: 'Access to the IED on which the IE app is installed.'",
            "sentence": "Access to the IED on which the IE app is installed."
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
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                sources = result.get('sources', [])
                
                print(f"\n✅ Response:")
                print(f"   Method: {method}")
                print(f"   AI Answer: \"{ai_answer}\"")
                print(f"   Suggestion: \"{suggestion}\"")
                print(f"   Sources: {len(sources)}")
                
                # Analyze issues
                print(f"\n📊 ISSUE ANALYSIS:")
                
                # Check truncation
                if "..." in ai_answer or "..." in suggestion:
                    print(f"   ❌ TRUNCATION: Response appears to be cut off")
                else:
                    print(f"   ✅ No truncation detected")
                
                # Check sources
                if not sources or any(str(source).find('undefined') != -1 for source in sources):
                    print(f"   ❌ SOURCES: Undefined or missing sources")
                    for j, source in enumerate(sources):
                        print(f"     Source {j+1}: {source}")
                else:
                    print(f"   ✅ Sources available")
                
                # Check passive voice logic
                sentence = test_case['sentence']
                has_passive_indicators = any(phrase in sentence.lower() for phrase in [
                    'must be', 'is installed', 'was', 'were', 'been', 'being'
                ])
                
                if has_passive_indicators:
                    print(f"   ⚠️ PASSIVE VOICE: Contains passive indicators")
                else:
                    print(f"   ✅ No clear passive voice found")
                
                # Check if suggestion provides improvement
                if len(suggestion) > len(sentence) + 10:
                    print(f"   ✅ IMPROVEMENT: Suggestion provides additional content")
                else:
                    print(f"   ❌ IMPROVEMENT: Suggestion doesn't seem to improve original")
                
                # Specific analysis per case
                if i == 1:  # Requirement statement
                    print(f"\n💡 CASE 1 ANALYSIS:")
                    print(f"   - 'must be met' is passive but often acceptable in requirements")
                    print(f"   - Better: 'Meet the following requirement:' or 'You must meet:'")
                    
                elif i == 2:  # IED access
                    print(f"\n💡 CASE 2 ANALYSIS:")
                    print(f"   - This is a noun phrase, not a complete sentence")
                    print(f"   - 'is installed' is passive but in a relative clause")
                    print(f"   - Better: 'Access the IED where you installed the IE app'")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_better_alternatives():
    """Test what better suggestions should look like."""
    
    print(f"\n\n🎯 TESTING BETTER ALTERNATIVES")
    print("=" * 35)
    
    better_cases = [
        {
            "feedback": "passive voice detected by rule",
            "sentence": "The file was uploaded by the user."
        },
        {
            "feedback": "passive voice detected by rule", 
            "sentence": "The system can be configured by administrators."
        }
    ]
    
    for case in better_cases:
        print(f"\n📝 Testing clear passive voice:")
        print(f"   Sentence: '{case['sentence']}'")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json=case,
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Method: {result.get('method')}")
                print(f"   AI Answer: \"{result.get('ai_answer', '')[:100]}...\"")
                print(f"   Suggestion: \"{result.get('suggestion', '')[:100]}...\"")
            
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_passive_voice_issues()
    test_better_alternatives()
    
    print(f"\n💡 SUMMARY OF ISSUES:")
    print(f"1. AI suggestions are being truncated with '...'")
    print(f"2. Knowledge sources showing 'undefined' instead of rule info")
    print(f"3. False positive passive voice detection on acceptable phrases")
    print(f"4. AI not providing complete alternative phrasings")
    print(f"5. Need better passive voice filtering logic")
