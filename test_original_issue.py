#!/usr/bin/env python3
"""
Test the original problem case through the full API
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_original_issue():
    """Test the exact case from the user's report"""
    
    # Original reported issue
    sentence = "Both options support backup files from the"
    feedback = "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'."
    
    print("=== Testing Original Issue ===")
    print(f"Original sentence: '{sentence}'")
    print(f"Writing Problem: {feedback}")
    print()
    
    # Get AI suggestion
    result = get_enhanced_ai_suggestion(feedback, sentence)
    
    print("AI Suggestion:")
    print(result['suggestion'])
    print()
    print(f"Method used: {result['method']}")
    print(f"Confidence: {result['confidence']}")
    
    # Verify it doesn't change the sentence incorrectly
    if "backing up" in result['suggestion'] or "back up your files" in result['suggestion']:
        print("❌ STILL BROKEN: AI incorrectly changed noun usage to verb")
    elif "No change needed" in result['suggestion']:
        print("✅ FIXED: AI correctly identified this as proper noun usage")
    else:
        print("⚠️  UNCLEAR: Need to check the result manually")

if __name__ == "__main__":
    test_original_issue()
