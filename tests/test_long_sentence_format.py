#!/usr/bin/env python3
"""
Test the new long sentence formatting to match user's desired output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_long_sentence_format():
    """Test that long sentences now show the user's preferred format."""
    
    print("🔧 TESTING NEW LONG SENTENCE FORMAT")
    print("=" * 60)
    
    # Test with the user's example sentence
    feedback = "Issue: Long sentence detected (27 words). Consider breaking this into shorter sentences for better readability."
    sentence = "Tag retention eliminates the need for repetitive tag selection, as the system automatically remembers and applies your previous choices, resulting in time and effort savings and a more streamlined workflow."
    
    print("Testing with user's example sentence...")
    print(f"Feedback: {feedback}")
    print(f"Sentence: {sentence[:60]}...")
    print()
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="technical",
            writing_goals=["clarity", "conciseness"]
        )
        
        if result and result.get('suggestion'):
            print("🎯 NEW AI SUGGESTION FORMAT:")
            print("-" * 40)
            print(result['suggestion'])
            print("-" * 40)
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 'unknown')}")
            
            # Check if the format matches user's preference
            suggestion_text = result['suggestion']
            if "OPTION 1 has sentence 1:" in suggestion_text and "sentence 2:" in suggestion_text:
                print("\n✅ SUCCESS: Format matches user's preference!")
                print("   - Uses 'OPTION X has sentence 1:..., sentence 2:...' format")
            else:
                print("\n❌ ISSUE: Format doesn't match user's preference")
                print("   - Expected 'OPTION X has sentence 1:..., sentence 2:...' format")
            
        else:
            print("❌ No suggestion generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_comparison():
    """Show before vs after format."""
    
    print("\n" + "=" * 60)
    print("📊 FORMAT COMPARISON")
    print("=" * 60)
    
    print("BEFORE (old format):")
    print("OPTION 1: Tag retention eliminates the need for repetitive tag selection.")
    print("OPTION 2: This includes applies your previous choices, resulting in time and effort savings.")
    print("OPTION 3: Complete both actions: tag retention eliminates the need...")
    
    print("\nAFTER (new format - user's preference):")
    print("OPTION 1 has sentence 1: Tag retention eliminates the need for repetitive tag selection, sentence 2: This allows the system to apply your previous choices automatically")
    print("OPTION 2 has sentence 1: The system remembers your tag choices automatically, sentence 2: This results in time savings and a more streamlined workflow")
    print("OPTION 3: Tag retention eliminates repetitive selection and the system applies your previous choices automatically")

if __name__ == "__main__":
    test_long_sentence_format()
    test_comparison()
    print("\n" + "=" * 60)
    print("🎯 Long sentence format testing completed!")
    print("=" * 60)
