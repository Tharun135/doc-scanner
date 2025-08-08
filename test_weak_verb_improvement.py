#!/usr/bin/env python3
"""
Test the improved weak verb construction rule to ensure it correctly handles
list introduction patterns.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_weak_verb_improvements():
    """Test the improved weak verb construction detection."""
    
    try:
        from app.rules.concise_simple_words import check
        
        # Test cases that should NOT be flagged (correct usage)
        correct_cases = [
            "There are three ways to configure the PROFINET IO Connector:",
            "There are two methods available for data export:",
            "There are several options for deployment:",
            "There are four key features in this release:",
            "There are multiple approaches to solving this problem:",
            "There are five steps required for installation:",
            "There are no issues with the current implementation.",
            "There are not any problems detected."
        ]
        
        # Test cases that SHOULD be flagged (weak usage)
        weak_cases = [
            "There are issues with the system",
            "There are problems",
            "There are benefits",
            "There are some concerns",
            "There are difficulties",
            "There are challenges"
        ]
        
        print("🧪 TESTING IMPROVED WEAK VERB CONSTRUCTION RULE")
        print("=" * 60)
        
        print("\n✅ TESTING CORRECT USAGE (should NOT be flagged):")
        print("-" * 50)
        
        for i, test_case in enumerate(correct_cases, 1):
            print(f"\n{i:2d}. {test_case}")
            suggestions = check(test_case)
            weak_verb_suggestions = [s for s in suggestions if "Weak verb construction" in s]
            
            if weak_verb_suggestions:
                print(f"    ❌ INCORRECTLY FLAGGED: {weak_verb_suggestions[0]}")
            else:
                print(f"    ✅ CORRECTLY NOT FLAGGED")
        
        print("\n\n❌ TESTING WEAK USAGE (should BE flagged):")
        print("-" * 50)
        
        for i, test_case in enumerate(weak_cases, 1):
            print(f"\n{i:2d}. {test_case}")
            suggestions = check(test_case)
            weak_verb_suggestions = [s for s in suggestions if "Weak verb construction" in s]
            
            if weak_verb_suggestions:
                print(f"    ✅ CORRECTLY FLAGGED: {weak_verb_suggestions[0]}")
            else:
                print(f"    ❌ INCORRECTLY NOT FLAGGED")
        
        print("\n" + "=" * 60)
        print("🎯 SPECIFIC USER CASE TEST:")
        user_case = "There are three ways to configure the PROFINET IO Connector:"
        print(f"'{user_case}'")
        
        suggestions = check(user_case)
        weak_verb_suggestions = [s for s in suggestions if "Weak verb construction" in s]
        
        if weak_verb_suggestions:
            print("❌ RESULT: This sentence would still be incorrectly flagged!")
            print(f"   Suggestion: {weak_verb_suggestions[0]}")
        else:
            print("✅ RESULT: This sentence is correctly NOT flagged!")
            print("   This is proper list introduction syntax.")
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weak_verb_improvements()
