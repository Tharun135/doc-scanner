#!/usr/bin/env python3
"""
Final comprehensive test of the complete backup/back up fix
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.rules.terminology_b_terms import check
from app.ai_improvement import get_enhanced_ai_suggestion

def test_complete_system():
    """Test the complete system from rule detection to AI suggestion"""
    
    print("=== COMPLETE SYSTEM TEST: Backup/Back Up ===")
    
    # Test the original problematic case
    sentence = "Both options support backup files from the"
    
    print(f"Test sentence: '{sentence}'")
    print()
    
    # Step 1: Check rule detection
    print("Step 1: Rule Detection")
    suggestions = check(sentence)
    backup_suggestions = [s for s in suggestions if 'back up' in s and 'verb' in s]
    
    if backup_suggestions:
        print("❌ RULE STILL BROKEN: Incorrectly flagged by detection rule")
        for suggestion in backup_suggestions:
            print(f"  - {suggestion}")
    else:
        print("✅ RULE FIXED: Not flagged by detection rule (correct)")
    
    print()
    
    # Step 2: Test AI suggestion (simulating what would happen if it WAS flagged)
    print("Step 2: AI Suggestion (if hypothetically flagged)")
    feedback = "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'."
    
    result = get_enhanced_ai_suggestion(feedback, sentence)
    print(f"AI Method: {result['method']}")
    print(f"AI Suggestion: {result['suggestion']}")
    
    if "No change needed" in result['suggestion']:
        print("✅ AI LOGIC CORRECT: Recognizes proper noun usage")
    else:
        print("❌ AI LOGIC ISSUE: Would make incorrect change")
    
    print()
    print("="*60)
    
    # Test a case that SHOULD be flagged
    print("\nTEST CASE: Should be flagged")
    verb_sentence = "Remember to backup your files regularly"
    print(f"Test sentence: '{verb_sentence}'")
    
    # Check rule detection
    verb_suggestions = check(verb_sentence)
    backup_verb_suggestions = [s for s in verb_suggestions if 'back up' in s and 'verb' in s]
    
    if backup_verb_suggestions:
        print("✅ RULE CORRECT: Properly flagged verb usage")
        
        # Test AI suggestion
        result = get_enhanced_ai_suggestion(backup_verb_suggestions[0], verb_sentence)
        print(f"AI Suggestion: {result['suggestion']}")
        
        if "back up your files" in result['suggestion']:
            print("✅ AI CORRECT: Properly converts to verb form")
        else:
            print("❌ AI ISSUE: Incorrect suggestion")
    else:
        print("❌ RULE ISSUE: Should have flagged verb usage")

if __name__ == "__main__":
    test_complete_system()
