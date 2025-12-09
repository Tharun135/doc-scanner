#!/usr/bin/env python3
"""
Test the document_first_ai function directly for the failing sentence
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_first_direct():
    print("🧪 Testing document_first_ai Directly for Tags Sentence")
    print("=" * 60)
    
    try:
        from app.document_first_ai import get_document_first_suggestion
        print("✅ Successfully imported document_first_ai")
        
        test_sentence = "Tags are added to the data source."
        feedback_text = f"Avoid passive voice in sentence: '{test_sentence}'"
        
        print(f"📝 Testing: '{test_sentence}'")
        print(f"📋 Feedback: '{feedback_text}'")
        print()
        
        # Call the enhanced function directly
        result = get_document_first_suggestion(
            feedback_text=feedback_text,
            sentence_context=test_sentence,
            document_type="technical",
            writing_goals=["clarity", "directness", "active_voice"]
        )
        
        print(f"📊 Direct Result: {result}")
        
        if result and result.get('success'):
            suggestion = result.get('suggestion', '').strip()
            method = result.get('method', 'N/A')
            confidence = result.get('confidence', 'N/A')
            
            print(f"\n✅ Success: {result.get('success')}")
            print(f"📊 Method: {method}")
            print(f"🎯 Confidence: {confidence}")
            print(f"💡 Suggestion: '{suggestion}'")
            print(f"📚 AI Answer: {result.get('ai_answer', 'N/A')[:200]}...")
            
            if suggestion != test_sentence:
                print(f"\n✅ CONVERSION DETECTED!")
                if "add tags" in suggestion.lower():
                    print("🎉 Correct conversion pattern found!")
                else:
                    print(f"⚠️ Different conversion: {suggestion}")
            else:
                print(f"\n❌ NO CONVERSION - Same text returned")
                print(f"❓ Confidence: {confidence} (might be why it's falling back)")
        else:
            print(f"❌ Failed or no success: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_first_direct()