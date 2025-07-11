#!/usr/bin/env python3
"""
Test the complete fix for the original issue
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.rules.terminology_b_terms import check

def test_original_sentence():
    """Test the original problematic sentence"""
    
    # The original sentence that was incorrectly flagged
    sentence = "Both options support backup files from the"
    
    print("=== Testing Original Problematic Sentence ===")
    print(f"Sentence: '{sentence}'")
    
    # Check if it gets flagged
    suggestions = check(sentence)
    backup_suggestions = [s for s in suggestions if 'back up' in s and 'verb' in s]
    
    print(f"Backup suggestions: {len(backup_suggestions)}")
    
    if backup_suggestions:
        print("❌ STILL BROKEN: Sentence is incorrectly flagged")
        for suggestion in backup_suggestions:
            print(f"  - {suggestion}")
    else:
        print("✅ FIXED: Sentence is correctly NOT flagged as having backup issues")
        print("This is proper noun/adjective usage and should not trigger the rule.")
    
    # Show all suggestions for context
    if suggestions:
        print(f"\nAll suggestions ({len(suggestions)}):")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    else:
        print("\nNo issues detected (as expected)")

if __name__ == "__main__":
    test_original_sentence()
