#!/usr/bin/env python3

"""
Detailed test to see exactly what's happening with punctuation detection.
"""

import sys
sys.path.append('app')

from app.rules.punctuation import _split_into_sentences, _check_hyphen_dash, _check_comma_usage, _check_colon_semicolon, _check_quotation_marks, _check_apostrophes

# Test sentences
test_sentences = [
    "This is a normal sentence.",
    "This sentence ends with a period.",
    "Multiple sentences. With periods. At the end.",
]

print("Testing detailed punctuation functions:")
print("=" * 60)

for text in test_sentences:
    print(f"\nOriginal text: '{text}'")
    
    # Test sentence splitting
    sentences = _split_into_sentences(text)
    print(f"Split sentences: {sentences}")
    
    # Test each function on each split sentence
    for i, sentence in enumerate(sentences):
        print(f"\n  Sentence {i+1}: '{sentence}'")
        
        comma_issues = _check_comma_usage(sentence)
        if comma_issues:
            print(f"    Comma issues: {comma_issues}")
        
        colon_issues = _check_colon_semicolon(sentence)
        if colon_issues:
            print(f"    Colon/semicolon issues: {colon_issues}")
        
        quote_issues = _check_quotation_marks(sentence)
        if quote_issues:
            print(f"    Quote issues: {quote_issues}")
        
        hyphen_issues = _check_hyphen_dash(sentence)
        if hyphen_issues:
            print(f"    Hyphen/dash issues: {hyphen_issues}")
        
        apostrophe_issues = _check_apostrophes(sentence)
        if apostrophe_issues:
            print(f"    Apostrophe issues: {apostrophe_issues}")
        
        if not any([comma_issues, colon_issues, quote_issues, hyphen_issues, apostrophe_issues]):
            print(f"    No issues found")

print("\n" + "=" * 60)
print("Test completed!")
