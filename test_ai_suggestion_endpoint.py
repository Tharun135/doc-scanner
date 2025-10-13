#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_ai_suggestion_endpoint():
    """Test the actual AI suggestion endpoint to see what it returns"""
    
    # Your exact case
    feedback_text = "Avoid passive voice in sentence: 'The following requirement must be met:'"
    sentence_context = "The following requirement must be met:"
    
    print("🔍 Testing AI Suggestion Endpoint")
    print("=" * 60)
    print(f"Feedback: {feedback_text}")
    print(f"Context: {sentence_context}")
    print("-" * 60)
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical",
            writing_goals=[],
            document_content="",
            option_number=1,
            issue=None
        )
        
        print("Result structure:")
        for key, value in result.items():
            print(f"  {key}: {value}")
            
        suggestion = result.get("suggestion", "")
        print(f"\nFinal suggestion text: '{suggestion}'")
        
        # Check for title case
        words = suggestion.split()
        title_case_words = []
        for i, word in enumerate(words):
            if i > 0 and word and len(word) > 1 and word[0].isupper() and word[1:].islower():
                if word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from']:
                    title_case_words.append(word)
        
        if title_case_words:
            print(f"⚠️ TITLE CASE DETECTED IN ENDPOINT: {title_case_words}")
        else:
            print("✅ No title case issues in endpoint response")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_suggestion_endpoint()
