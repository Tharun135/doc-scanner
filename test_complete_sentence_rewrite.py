#!/usr/bin/env python3
"""
Test complete sentence rewrite functionality
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from ai_improvement import GeminiAISuggestionEngine

def test_complete_sentence_rewrites():
    """Test that AI suggestions provide complete sentence rewrites"""
    print("🔍 Testing Complete Sentence Rewrite Functionality...")
    print("=" * 60)
    
    engine = GeminiAISuggestionEngine()
    
    test_cases = [
        {
            "name": "Passive Voice in Long Sentence",
            "issue": "Passive voice detected",
            "sentence": "The document was carefully reviewed by the team and several important changes were made to improve clarity."
        },
        {
            "name": "First Person in Instruction",
            "issue": "Avoid first person in technical writing",
            "sentence": "We recommend that you backup your files before proceeding with the installation process."
        },
        {
            "name": "Modal Verb Issue",
            "issue": "Modal verb usage: 'may' for permission",
            "sentence": "You may now click the Save button to save your work and exit the application."
        },
        {
            "name": "Long Sentence",
            "issue": "Sentence too long",
            "sentence": "When you are working with multiple documents simultaneously and need to ensure that all changes are properly saved before closing the application, it is important to remember to use the auto-save feature."
        }
    ]
    
    for test in test_cases:
        print(f"📝 Test: {test['name']}")
        print(f"Issue: {test['issue']}")
        print(f"Original: '{test['sentence']}'")
        print("-" * 50)
        
        try:
            result = engine.generate_contextual_suggestion(
                feedback_text=test['issue'],
                sentence_context=test['sentence'],
                document_type="technical"
            )
            
            if result and result.get('suggestion'):
                print(f"Method: {result.get('method', 'unknown')}")
                print(f"AI Suggestion: {result['suggestion']}")
                
                # Check if it looks like complete sentence rewrites
                suggestion = result['suggestion']
                if 'OPTION 1:' in suggestion and 'OPTION 2:' in suggestion:
                    print("✅ Multiple options provided")
                else:
                    print("⚠️ Format may not be correct")
                    
                print(f"✅ Using {result.get('method', 'unknown')}")
            else:
                print("❌ No suggestion generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_complete_sentence_rewrites()
