#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import LlamaIndexAISuggestionEngine

def test_passive_voice_suggestions():
    print("="*80)
    print("TESTING PASSIVE VOICE AI SUGGESTIONS")
    print("="*80)
    
    ai_manager = LlamaIndexAISuggestionEngine()
    
    # Test the specific problematic sentence
    test_sentence = "These values are derived during the XSLT Transformation step in Model Maker."
    feedback = "Convert to active voice: 'These values get derived during the XSLT Transformation step in Model Maker.'"
    
    print(f"Original sentence: {test_sentence}")
    print(f"Feedback: {feedback}")
    print("-" * 50)
    
    try:
        result = ai_manager.generate_contextual_suggestion(feedback, test_sentence)
        print("AI Suggestion Result:")
        print(f"Suggestion: {result.get('suggestion', 'No suggestion')}")
        print("-" * 50)
        
        # Parse and analyze options
        suggestion_text = result.get('suggestion', '')
        lines = suggestion_text.split('\n')
        options = [line for line in lines if line.startswith('OPTION')]
        
        print("Analysis:")
        for i, option in enumerate(options, 1):
            print(f"  Option {i}: {option}")
            
            # Check for issues
            if "get derived" in option.lower():
                print(f"    ❌ Issue: Still uses 'get derived' (same as original)")
            elif "are derived" in option.lower():
                print(f"    ❌ Issue: Still passive voice")
            elif option.count("are derived") > 1:
                print(f"    ❌ Issue: Grammatical error/repetition")
            elif "users can update" in option.lower():
                print(f"    ❌ Issue: Uses 'Users' instead of 'You'")
            else:
                print(f"    ✅ Good: Active voice conversion")
                
        # Check for "User" vs "You" 
        if "User" in suggestion_text and "You" not in suggestion_text:
            print("  ❌ Issue: Uses 'User' instead of 'You'")
        elif "You" in suggestion_text:
            print("  ✅ Good: Uses 'You' instead of 'User'")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_passive_voice_suggestions()
