#!/usr/bin/env python3
"""
Test the modified punctuation rule to exclude colons
"""

from app.rules.punctuation_fixed import check

def test_colon_exclusion():
    print("=== TESTING COLON EXCLUSION FOR MISSING PUNCTUATION ===\n")
    
    # Test cases that should NOT be flagged (sentences ending with colon)
    should_not_flag = [
        "Prerequisite:",
        "Requirements:",
        "Steps:",
        "Note:",
        "Important:",
        "The following items are required:",
        "Please review the following:",
        "Configuration settings:",
        "Available options:",
    ]
    
    # Test cases that SHOULD still be flagged (missing punctuation)
    should_flag = [
        "This sentence is missing punctuation",
        "Another example without ending",
        "The document was reviewed",
        "Please save the file",
        "Configuration is complete",
    ]
    
    # Test cases that should NOT be flagged (proper punctuation)
    should_not_flag_proper = [
        "This sentence has proper punctuation.",
        "This is a question?",
        "What an exclamation!",
        "Short title",  # Should be excluded as title
        "Main Heading",  # Should be excluded as title
    ]
    
    print("🟢 TESTING SENTENCES WITH COLONS (should NOT be flagged):")
    all_correct = True
    
    for i, sentence in enumerate(should_not_flag, 1):
        results = check(sentence)
        punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ {i}. INCORRECTLY FLAGGED: '{sentence}'")
            for issue in punctuation_issues:
                print(f"    - {issue['message']}")
            all_correct = False
        else:
            print(f"✅ {i}. Correctly allowed: '{sentence}'")
    
    print(f"\n🔴 TESTING SENTENCES MISSING PUNCTUATION (should be flagged):")
    
    for i, sentence in enumerate(should_flag, 1):
        results = check(sentence)
        punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"✅ {i}. Correctly flagged: '{sentence}'")
        else:
            print(f"❌ {i}. INCORRECTLY ALLOWED: '{sentence}'")
            all_correct = False
    
    print(f"\n🟡 TESTING SENTENCES WITH PROPER PUNCTUATION (should NOT be flagged):")
    
    for i, sentence in enumerate(should_not_flag_proper, 1):
        results = check(sentence)
        punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ {i}. INCORRECTLY FLAGGED: '{sentence}'")
            all_correct = False
        else:
            print(f"✅ {i}. Correctly allowed: '{sentence}'")
    
    print(f"\n{'='*60}")
    if all_correct:
        print("🎉 ALL TESTS PASSED! The punctuation rule is working correctly.")
        print("✅ Sentences ending with colons are now allowed")
        print("✅ Sentences missing punctuation are still flagged")
        print("✅ Sentences with proper punctuation are still allowed")
    else:
        print("⚠️  Some tests failed. The rule may need further adjustment.")

def test_specific_example():
    print("\n=== TESTING SPECIFIC EXAMPLE ===\n")
    
    # Test the user's likely scenario
    examples = [
        "Prerequisite:",
        "The WinCC Unified Runtime app must be running",
        "A project must be added as described in Add Project",
    ]
    
    for sentence in examples:
        print(f"Testing: '{sentence}'")
        results = check(sentence)
        punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ FLAGGED for missing punctuation:")
            for issue in punctuation_issues:
                print(f"   - '{issue['text']}' - {issue['message']}")
        else:
            print(f"✅ No missing punctuation issues")
        print()

if __name__ == "__main__":
    test_colon_exclusion()
    test_specific_example()
