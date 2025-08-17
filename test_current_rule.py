#!/usr/bin/env python3
"""
Test the current rule with the user's exact sentences
"""

from app.rules.formatting_fixed import check, _looks_like_list_item

def test_user_sentences():
    print("=== TESTING USER'S EXACT SENTENCES ===\n")
    
    # The user's sentences that are being flagged
    user_sentences = [
        "The WinCC Unified Runtime app must be running.",  # This might have a space before period
        "A project must be added as described in Add Project.",
        "The WinCC Unified Runtime app must be running .",  # With space before period
        "A project must be added as described in Add Project .",  # With space before period
    ]
    
    for i, sentence in enumerate(user_sentences, 1):
        print(f"SENTENCE {i}: '{sentence}'")
        print(f"Has space before punctuation: {sentence.endswith(' .')}")
        print(f"Looks like list item: {_looks_like_list_item(sentence)}")
        
        # Test the formatting rule
        results = check(sentence)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ FLAGGED: {len(punctuation_issues)} issues")
            for issue in punctuation_issues:
                print(f"   - '{issue['text']}' at {issue['start']}-{issue['end']}")
        else:
            print(f"✅ NOT FLAGGED: Allowed as list item")
        print("-" * 60)

def test_pattern_matching():
    print("\n=== TESTING PATTERN MATCHING ===\n")
    
    test_sentence = "The WinCC Unified Runtime app must be running ."
    print(f"Testing: '{test_sentence}'")
    
    # Check each pattern in the list_indicators (updated patterns)
    import re
    list_indicators = [
        r'^(The|A|An)\s+\w+(?:\s+\w+)*\s+(must|should|will|can|may|is|are)',
        r'^(Download|Install|Open|Close|Save|Create|Delete|Configure|Setup|Set up)',
        r'^(Click|Select|Choose|Enter|Type|Navigate|Browse|Search)',
        r'^(Ensure|Verify|Check|Confirm|Make sure)',
        r'^(Add|Remove|Edit|Modify|Update|Change)',
        r'^(This|That|It)\s+(is|will|should|must|can|may)\s+(required|needed|necessary)',
        r'^(First|Second|Third|Next|Then|Finally|Last)',
        r'^(Required|Optional|Important|Note|Warning)',
        r'^(The\s+\w+(?:\s+\w+)*\s+(application|app|system|software|program|tool))',
        r'^(A\s+(project|file|document|configuration|setting))',
    ]
    
    print("Pattern matching results:")
    for i, pattern in enumerate(list_indicators, 1):
        match = re.match(pattern, test_sentence, re.IGNORECASE)
        print(f"{i:2d}. {pattern}")
        print(f"    Match: {'✅ YES' if match else '❌ NO'}")
        if match:
            print(f"    Matched: '{match.group()}'")
        print()

if __name__ == "__main__":
    test_user_sentences()
    test_pattern_matching()
