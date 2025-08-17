#!/usr/bin/env python3
"""
Test the improved formatting rule with individual sentences
"""

from app.rules.formatting_fixed import check as check_formatting

def test_individual_sentences():
    print("=== TESTING IMPROVED RULE WITH INDIVIDUAL SENTENCES ===\n")
    
    # Test sentences that should be ALLOWED (list item patterns)
    list_sentences = [
        "The WinCC Unified Runtime app must be running .",
        "A project must be added as described in Add Project .",
        "The system must be configured properly .",
        "Download the latest version of the software .",
        "Open the configuration dialog .",
        "Click the Save button .",
        "Ensure all settings are correct .",
        "First, configure the network settings .",
        "This is required for proper operation .",
        "The application will start automatically .",
    ]
    
    # Test sentences that should still be FLAGGED (regular text)
    regular_sentences = [
        "This is wrong . It's not a list item.",
        "Hello , world",
        "What ? This should be flagged.",
        "The meeting ended early . Everyone left.",
        "I think , therefore I am .",
    ]
    
    print("LIST-LIKE SENTENCES (should be ALLOWED):")
    for i, sentence in enumerate(list_sentences, 1):
        print(f"\n{i}. Sentence: '{sentence}'")
        results = check_formatting(sentence)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if space_issues:
            print(f"   ❌ STILL FLAGGED: {len(space_issues)} issues")
            for issue in space_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ✅ ALLOWED: No space issues")
    
    print("\n" + "="*60)
    print("REGULAR SENTENCES (should still be FLAGGED):")
    
    for i, sentence in enumerate(regular_sentences, 1):
        print(f"\n{i}. Sentence: '{sentence}'")
        results = check_formatting(sentence)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if space_issues:
            print(f"   ✅ CORRECTLY FLAGGED: {len(space_issues)} issues")
            for issue in space_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ❌ SHOULD BE FLAGGED: No space issues found")

def test_specific_user_case():
    print("\n" + "="*60)
    print("TESTING USER'S SPECIFIC SENTENCES:")
    
    user_sentences = [
        "The WinCC Unified Runtime app must be running .",
        "A project must be added as described in Add Project .",
    ]
    
    for i, sentence in enumerate(user_sentences, 1):
        print(f"\nSentence {i}: '{sentence}'")
        results = check_formatting(sentence)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if space_issues:
            print(f"   ❌ PROBLEM: Still flagged with {len(space_issues)} issues")
            for issue in space_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"   ✅ FIXED: No longer flagged!")

if __name__ == "__main__":
    test_individual_sentences()
    test_specific_user_case()
