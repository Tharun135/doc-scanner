#!/usr/bin/env python3
"""
Test enhanced fallback system for complete sentence rewrites
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from ai_improvement import GeminiAISuggestionEngine

def test_fallback_sentence_rewrites():
    """Test that fallback system provides complete sentence rewrites"""
    print("🔍 Testing Enhanced Fallback System...")
    print("=" * 60)
    
    engine = GeminiAISuggestionEngine()
    
    test_cases = [
        {
            "name": "Passive Voice",
            "issue": "Passive voice detected",
            "sentence": "The document was carefully reviewed by the team and several changes were made."
        },
        {
            "name": "First Person",
            "issue": "Avoid first person in technical writing",
            "sentence": "We recommend that you backup your files before proceeding."
        },
        {
            "name": "Modal Verb",
            "issue": "Modal verb usage: 'may' for permission",
            "sentence": "You may now click the Save button to complete the process."
        },
        {
            "name": "Long Sentence",
            "issue": "Sentence too long",
            "sentence": "When you are working with multiple documents and need to save changes, it is important to use the auto-save feature."
        }
    ]
    
    for test in test_cases:
        print(f"📝 Test: {test['name']}")
        print(f"Issue: {test['issue']}")
        print(f"Original: '{test['sentence']}'")
        print("-" * 50)
        
        # Force fallback by calling directly
        result = engine.generate_minimal_fallback(
            feedback_text=test['issue'],
            sentence_context=test['sentence']
        )
        
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Suggestion:\n{result['suggestion']}")
        
        # Check if it looks like complete sentence rewrites
        suggestion = result['suggestion']
        if 'OPTION 1:' in suggestion and 'OPTION 2:' in suggestion:
            print("✅ Multiple options provided")
        if 'WHY:' in suggestion:
            print("✅ Explanation provided")
        
        print(f"✅ Using {result.get('method', 'unknown')}")
        print()

if __name__ == "__main__":
    test_fallback_sentence_rewrites()
