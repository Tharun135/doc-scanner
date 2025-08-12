#!/usr/bin/env python3
"""Test the specific passive voice conversion issue."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_passive_voice_conversion():
    """Test the 'must be met' conversion specifically."""
    
    # Test the specific sentence that was problematic
    test_sentence = "The following requirement must be met:"
    
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        print(f"Testing: '{test_sentence}'")
        print("="*50)
        
        result = get_enhanced_ai_suggestion(
            feedback_text="Convert to active voice",
            sentence_context=test_sentence
        )
        
        print(f"Method: {result.get('method')}")
        print(f"Confidence: {result.get('confidence')}")
        print("\nSuggestion:")
        print(result.get('suggestion', ''))
        
        # Check if the result is meaningful
        suggestion = result.get('suggestion', '')
        if 'OPTION 1:' in suggestion:
            lines = suggestion.split('\n')
            option1 = lines[0] if lines else ''
            
            if 'The following requirement must be met:' in option1:
                print("\n❌ ISSUE: Option 1 is identical to original")
            else:
                print("\n✅ GOOD: Option 1 provides a real alternative")
                
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_passive_voice_conversion()
