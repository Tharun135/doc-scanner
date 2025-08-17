#!/usr/bin/env python3
"""
Test specific sentence against clarity rules
"""

from app.rules.clarity_fixed import check

def test_sentence():
    sentence = "Autostart feature is beneficial in cases where an application or an IED is restarted."
    print(f"Testing sentence: {sentence}")
    print(f"Word count: {len(sentence.split())}")
    print()

    # Run the clarity check
    results = check(sentence)
    print(f"Number of issues found: {len(results)}")
    print()

    for i, result in enumerate(results, 1):
        print(f"Issue {i}:")
        print(f"  Text: '{result.get('text', 'N/A')}'")
        print(f"  Message: {result.get('message', 'N/A')}")
        print(f"  Start: {result.get('start', 'N/A')}")
        print(f"  End: {result.get('end', 'N/A')}")
        print()

    # Test the specific regex pattern for long sentences
    import re
    long_sentence_pattern = r'[A-Z][^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*[.!?]'
    
    match = re.search(long_sentence_pattern, sentence)
    print(f"Long sentence regex match: {match is not None}")
    if match:
        print(f"  Matched text: '{match.group(0)}'")
        print(f"  Start: {match.start()}, End: {match.end()}")

if __name__ == "__main__":
    test_sentence()
