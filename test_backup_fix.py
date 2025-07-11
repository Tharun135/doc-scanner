#!/usr/bin/env python3
"""
Test the backup/back up fix with the full AI suggestion engine
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.ai_improvement import EnhancedAISuggestionEngine

def test_backup_fix():
    """Test the backup fix"""
    ai = EnhancedAISuggestionEngine()
    
    # Test case 1: Noun usage (should NOT change)
    sentence1 = "Both options support backup files from the"
    feedback1 = "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'."
    
    print("=== Test Case 1: Noun Usage (should NOT change) ===")
    print(f"Sentence: '{sentence1}'")
    print(f"Feedback: '{feedback1}'")
    
    result1 = ai.generate_contextual_suggestion(feedback1, sentence1)
    print(f"Method: {result1['method']}")
    print(f"Suggestion: {result1['suggestion']}")
    print()
    
    # Test case 2: Verb usage (should change)
    sentence2 = "Remember to backup your files regularly"
    feedback2 = "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'."
    
    print("=== Test Case 2: Verb Usage (should change) ===")
    print(f"Sentence: '{sentence2}'")
    print(f"Feedback: '{feedback2}'")
    
    result2 = ai.generate_contextual_suggestion(feedback2, sentence2)
    print(f"Method: {result2['method']}")
    print(f"Suggestion: {result2['suggestion']}")
    print()
    
    # Test case 3: Another noun usage
    sentence3 = "The backup strategy includes daily snapshots"
    feedback3 = "backup terminology"
    
    print("=== Test Case 3: Another Noun Usage ===")
    print(f"Sentence: '{sentence3}'")
    print(f"Feedback: '{feedback3}'")
    
    result3 = ai.generate_contextual_suggestion(feedback3, sentence3)
    print(f"Method: {result3['method']}")
    print(f"Suggestion: {result3['suggestion']}")
    print()

if __name__ == "__main__":
    test_backup_fix()
