#!/usr/bin/env python3
"""
Test script to demonstrate the improved weak verb detection in concise_simple_words.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import app.rules.concise_simple_words as concise_simple_words

def test_weak_verb_improvements():
    """Test the improved weak verb detection logic."""
    
    print("=== Testing Improved Weak Verb Detection ===\n")
    
    # Test cases that should NOT be flagged (appropriate use of 'be' and 'have')
    appropriate_cases = [
        "The server is running properly.",
        "The file is located in the Documents folder.",
        "This feature is available in version 2.0.",
        "You have two options for configuration.",
        "The system has completed the backup process.",
        "Users have reported improved performance."
    ]
    
    # Test cases that SHOULD be flagged (weak constructions)
    weak_constructions = [
        "There are three steps to follow.",
        "There is a problem with the connection.",
        "It is important to save your work regularly.",
        "It is possible to configure this setting.",
        "Users have the ability to customize the interface.",
        "You have the option to enable notifications."
    ]
    
    print("✅ APPROPRIATE USES (should NOT be flagged):")
    for i, text in enumerate(appropriate_cases, 1):
        print(f"\nTest {i}: '{text}'")
        suggestions = concise_simple_words.check(text)
        weak_suggestions = [s for s in suggestions if "weak verb" in s.lower() or "verb construction" in s.lower()]
        
        if weak_suggestions:
            print(f"  ❌ INCORRECTLY FLAGGED: {weak_suggestions[0][:100]}...")
        else:
            print(f"  ✅ CORRECTLY ALLOWED (no weak verb warnings)")
    
    print("\n" + "="*70)
    print("\n❌ WEAK CONSTRUCTIONS (should be flagged):")
    for i, text in enumerate(weak_constructions, 1):
        print(f"\nTest {i}: '{text}'")
        suggestions = concise_simple_words.check(text)
        weak_suggestions = [s for s in suggestions if "weak verb" in s.lower() or "verb construction" in s.lower()]
        
        if weak_suggestions:
            print(f"  ✅ CORRECTLY FLAGGED:")
            for suggestion in weak_suggestions:
                print(f"    {suggestion}")
        else:
            print(f"  ❌ MISSED: Should have been flagged but wasn't")
    
    print("\n" + "="*70)
    print("\n📝 SUMMARY:")
    print("The improved rule now focuses on:")
    print("✅ Specific weak patterns like 'there are/is', 'it is [adjective] to'")
    print("✅ Wordy constructions like 'have the ability to'")
    print("✅ Structured suggestions with Issue/Original/AI suggestion format")
    print("❌ No longer flags all instances of 'be' and 'have' verbs")
    print("❌ Avoids false positives for legitimate state descriptions")

if __name__ == "__main__":
    test_weak_verb_improvements()
