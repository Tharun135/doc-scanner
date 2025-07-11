#!/usr/bin/env python3
"""
Test script to debug the backup/back up issue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.ai_improvement import EnhancedAISuggestionEngine

def test_backup_debug():
    """Test the specific backup issue"""
    ai = EnhancedAISuggestionEngine()
    
    # Test the problematic sentence
    sentence = "Both options support backup files from the"
    feedback = "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'."
    
    print(f"Testing sentence: '{sentence}'")
    print(f"With feedback: '{feedback}'")
    
    result = ai.generate_smart_fallback_suggestion(feedback, sentence)
    print(f"Result: {result}")
    print()
    
    # Test with different feedback patterns that might trigger this
    test_feedbacks = [
        "backup",
        "back up", 
        "backup files",
        "Use 'back up' as a verb",
        "backup terminology"
    ]
    
    for test_feedback in test_feedbacks:
        print(f"Testing feedback: '{test_feedback}'")
        result = ai.generate_smart_fallback_suggestion(test_feedback, sentence)
        print(f"Result: {result}")
        print("-" * 50)

if __name__ == "__main__":
    test_backup_debug()
