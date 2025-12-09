#!/usr/bin/env python3
"""
Test the improved adverb handling for 'only' misplacement issues
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, '.')

from standalone_smart_suggestions import generate_smart_ai_suggestion

def test_only_adverb_case():
    """Test the specific 'only' adverb case from user feedback"""
    
    # Test the exact case reported
    feedback_text = "Check use of adverb: 'only' in sentence 'In the IEM, you only get a very general overview about the CPU load of an app.'"
    sentence = "In the IEM, you only get a very general overview about the CPU load of an app."
    
    print("🧠 Testing 'only' adverb misplacement...")
    print(f"📝 Original sentence: {sentence}")
    print(f"🔍 Feedback: {feedback_text}")
    print()
    
    result = generate_smart_ai_suggestion(feedback_text, sentence)
    
    if result:
        print("✅ Smart suggestion generated!")
        print(f"💡 Improved sentence: {result['suggestion']}")
        print(f"📚 AI explanation: {result['ai_answer']}")
        print(f"🎯 Confidence: {result['confidence']}")
        print(f"🔧 Method: {result['method']}")
        print(f"📖 Sources: {result['sources']}")
        print(f"✨ Success: {result['success']}")
    else:
        print("❌ No smart suggestion generated")
    
    print("\n" + "="*50)
    
    # Test additional cases
    test_cases = [
        {
            "feedback": "Check use of adverb: 'only' in sentence 'Only available in premium version, users can access this feature.'",
            "sentence": "Only available in premium version, users can access this feature."
        },
        {
            "feedback": "Check use of adverb: 'only' in sentence 'You only have access to basic functions.'",
            "sentence": "You only have access to basic functions."
        },
        {
            "feedback": "Check use of adverb: 'only' in sentence 'The system only shows critical alerts.'",
            "sentence": "The system only shows critical alerts."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"📝 Original: {test_case['sentence']}")
        
        result = generate_smart_ai_suggestion(test_case['feedback'], test_case['sentence'])
        
        if result:
            print(f"💡 Improved: {result['suggestion']}")
            print(f"📚 Explanation: {result['ai_answer'][:100]}...")
        else:
            print("❌ No suggestion generated")

if __name__ == "__main__":
    test_only_adverb_case()