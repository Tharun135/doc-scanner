#!/usr/bin/env python3
"""
Debug what the actual AI response looks like for long sentence splitting.
"""

import requests

def debug_ai_response():
    """Debug the actual AI response for sentence splitting."""
    
    print("🔍 DEBUGGING ACTUAL AI RESPONSE")
    print("=" * 35)
    
    # Test the exact scenario
    test_data = {
        'feedback': 'Consider breaking this long sentence into shorter ones',
        'sentence': "The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem."
    }
    
    print(f"📝 Testing with:")
    print(f"   Feedback: '{test_data['feedback']}'")
    print(f"   Original: '{test_data['sentence']}'")
    
    try:
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            method = result.get('method', 'unknown')
            ai_answer = result.get('ai_answer', '')
            suggestion = result.get('suggestion', '')
            
            print(f"\n✅ Response received:")
            print(f"   Method: {method}")
            print(f"   AI Answer: \"{ai_answer}\"")
            print(f"   Suggestion: \"{suggestion}\"")
            
            # Analysis
            print(f"\n📊 ANALYSIS:")
            print(f"   AI Answer length: {len(ai_answer)} chars")
            print(f"   Suggestion length: {len(suggestion)} chars")
            print(f"   AI Answer == Suggestion: {ai_answer == suggestion}")
            
            # Check for sentence splitting patterns
            if ai_answer:
                print(f"\n🔍 AI Answer contains:")
                print(f"   'Sentence 1:': {'Sentence 1:' in ai_answer}")
                print(f"   'Sentence 2:': {'Sentence 2:' in ai_answer}")
                print(f"   Multiple periods: {ai_answer.count('.') >= 2}")
                print(f"   Lines: {len(ai_answer.split(chr(10)))}")
                
                # Show each line
                lines = ai_answer.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        print(f"   Line {i+1}: \"{line.strip()}\"")
            
            # Expected vs actual
            print(f"\n💡 EXPECTED:")
            print(f"   The AI should provide 2 separate sentences")
            print(f"   Example: 'The IE Hub is a repository. It stores apps from Siemens.'")
            
            print(f"\n🎯 ACTUAL BEHAVIOR:")
            if len(suggestion.split('.')) >= 2:
                sentences = [s.strip() for s in suggestion.split('.') if s.strip()]
                print(f"   Found {len(sentences)} sentences:")
                for i, sent in enumerate(sentences, 1):
                    print(f"   {i}. \"{sent}.\"")
            else:
                print(f"   Only 1 sentence found - not properly split")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_ai_response()
    
    print(f"\n💡 DEBUGGING INSIGHTS:")
    print(f"   - If AI Answer is single sentence, the AI isn't following prompt")
    print(f"   - If Suggestion == AI Answer, extraction logic isn't working") 
    print(f"   - If no 'Sentence 1:' patterns, prompt needs adjustment")
    print(f"   - Need to check if fallback logic is being triggered")
