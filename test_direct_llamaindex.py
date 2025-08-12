#!/usr/bin/env python3
"""
Test the llamaindex_ai directly for the "must be met" fix
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from llamaindex_ai import get_ai_suggestion

def test_direct_llamaindex():
    """Test the llamaindex_ai directly"""
    
    print("🔍 Testing llamaindex_ai directly...")
    print("=" * 60)
    
    # Test the exact scenario from the user's report
    feedback_text = "Convert to active voice: 'The following requirement must be met:'"
    sentence_context = "The following requirement must be met:"
    
    print(f"📋 Issue: {feedback_text}")
    print(f"Original sentence: \"{sentence_context}\"")
    print("-" * 60)
    
    # Get the AI suggestion using the direct function
    result = get_ai_suggestion(
        feedback_text=feedback_text,
        sentence_context=sentence_context,
        document_type="technical",
        writing_goals=["clarity", "active_voice"]
    )
    
    suggestion = result.get("suggestion", "No suggestion generated")
    method = result.get("method", "unknown")
    
    print("AI Suggestion:")
    print(suggestion)
    print(f"\nMethod used: {method}")
    print("-" * 60)
    
    # Check for the specific broken patterns that were reported
    broken_patterns = [
        "system handles following requirement must be met",
        "users can update following requirement must be met",
        "The system handles following requirement must be met"
    ]
    
    suggestion_lower = suggestion.lower()
    broken_found = []
    
    for pattern in broken_patterns:
        if pattern.lower() in suggestion_lower:
            broken_found.append(pattern)
    
    # Check for good patterns
    good_patterns = [
        "you must meet the following requirement",
        "needs to be satisfied",
        "ensure the following requirement is met"
    ]
    
    good_found = []
    for pattern in good_patterns:
        if pattern.lower() in suggestion_lower:
            good_found.append(pattern)
    
    print("🔍 Analysis:")
    print(f"  ❌ Broken patterns found: {len(broken_found)}")
    for pattern in broken_found:
        print(f"     - '{pattern}'")
    
    print(f"  ✅ Good patterns found: {len(good_found)}")
    for pattern in good_found:
        print(f"     - '{pattern}'")
    
    # Overall assessment
    is_fixed = len(broken_found) == 0 and len(good_found) > 0
    
    print(f"\n🎯 Result: {'✅ FIXED - No more broken patterns!' if is_fixed else '❌ STILL BROKEN'}")
    
    return is_fixed

if __name__ == "__main__":
    print("Testing llamaindex_ai directly for the reported issue...")
    is_fixed = test_direct_llamaindex()
    
    if is_fixed:
        print("\n🎉 SUCCESS! The issue has been completely resolved in llamaindex_ai.py.")
        print("   The AI suggestions no longer contain broken grammar patterns.")
    else:
        print("\n💥 PROBLEM! The issue still exists and needs more fixes.")
    
    sys.exit(0 if is_fixed else 1)
