#!/usr/bin/env python3
"""
Simple test to demonstrate the apostrophe rule's behavior with clear examples.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules import special_characters

def demonstrate_apostrophe_rule():
    print("=== Apostrophe Rule Demonstration ===")
    print("The rule allows apostrophes for possession (the 'of' relationship) but warns against plural misuse.\n")
    
    # Possession examples (should be allowed)
    print("✅ VALID POSSESSION EXAMPLES ('of' relationship):")
    possession_examples = [
        ("Tharun's laptop", "laptop of Tharun"),
        ("The user's manual", "manual of the user"),
        ("Company's policy", "policy of the company"),
        ("Sarah's documentation", "documentation of Sarah")
    ]
    
    for possessive, of_form in possession_examples:
        text = f"{possessive} is available."
        suggestions = special_characters.check(text)
        apostrophe_warnings = [s for s in suggestions if "apostrophe" in s.lower()]
        status = "✅ Correctly allowed" if not apostrophe_warnings else "❌ Incorrectly flagged"
        print(f"  '{possessive}' = '{of_form}' → {status}")
    
    # Plural misuse examples (should be flagged)
    print("\n❌ PLURAL MISUSE EXAMPLES (should be flagged):")
    plural_examples = [
        ("API's are important", "APIs are important"),
        ("The application's have features", "The applications have features"),
        ("System's are running", "Systems are running")
    ]
    
    for wrong_form, correct_form in plural_examples:
        suggestions = special_characters.check(wrong_form)
        apostrophe_warnings = [s for s in suggestions if "apostrophe" in s.lower()]
        if apostrophe_warnings:
            print(f"  '{wrong_form}' → ✅ Correctly flagged")
            print(f"    Suggestion: {apostrophe_warnings[0][:100]}...")
        else:
            print(f"  '{wrong_form}' → ❌ Should be flagged but wasn't")

if __name__ == "__main__":
    demonstrate_apostrophe_rule()
