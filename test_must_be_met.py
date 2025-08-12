#!/usr/bin/env python3
"""
Test script for "must be met" pattern fix
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from llamaindex_ai import llamaindex_ai_engine

def test_must_be_met_pattern():
    """Test the specific 'must be met' pattern that was failing"""
    
    print("🧪 Testing 'must be met' pattern...")
    print("=" * 50)
    
    # Test the exact sentence from the user's report
    test_sentence = "The following requirement must be met:"
    feedback = "Convert to active voice"
    
    print(f"Input: '{test_sentence}'")
    print(f"Feedback: '{feedback}'")
    print("-" * 50)
    
    # Get AI suggestion
    result = llamaindex_ai_engine.generate_contextual_suggestion(
        feedback_text=feedback,
        sentence_context=test_sentence,
        document_type="technical",
        writing_goals=["clarity", "active_voice"]
    )
    
    suggestion = result.get("suggestion", "")
    print("AI Suggestion:")
    print(suggestion)
    print("-" * 50)
    
    # Check for broken patterns
    broken_patterns = [
        "system handles following requirement must be met",
        "users can update following requirement must be met",
        "following requirement must be met:",  # This would be in a malformed option
    ]
    
    suggestion_lower = suggestion.lower()
    has_broken_pattern = any(pattern in suggestion_lower for pattern in broken_patterns)
    
    # Check for proper option format
    has_proper_options = "OPTION 1:" in suggestion and "OPTION 2:" in suggestion and "OPTION 3:" in suggestion
    has_why_explanation = "WHY:" in suggestion
    
    print("✅ Validation Results:")
    print(f"  - Has proper option format: {'✅' if has_proper_options else '❌'}")
    print(f"  - Has WHY explanation: {'✅' if has_why_explanation else '❌'}")
    print(f"  - No broken patterns: {'✅' if not has_broken_pattern else '❌'}")
    
    if has_broken_pattern:
        print(f"  ❌ Found broken patterns in suggestion!")
        for pattern in broken_patterns:
            if pattern in suggestion_lower:
                print(f"     - Found: '{pattern}'")
    
    # Test success criteria
    success = (
        has_proper_options and 
        has_why_explanation and 
        not has_broken_pattern and
        "you must meet the following requirement" in suggestion_lower
    )
    
    print(f"\n🎯 Overall Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    print("Testing specific 'must be met' pattern fix...")
    success = test_must_be_met_pattern()
    
    if success:
        print("\n🎉 Test PASSED! The 'must be met' pattern is now fixed.")
    else:
        print("\n💥 Test FAILED! The pattern still has issues.")
    
    sys.exit(0 if success else 1)
