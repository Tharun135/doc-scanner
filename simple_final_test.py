#!/usr/bin/env python3
"""
Simple final test for the formatting rule fix
"""

from app.rules.formatting_fixed import check

def simple_final_test():
    print("=== SIMPLE FINAL TEST ===\n")
    
    # Your exact sentences
    user_sentences = [
        "The WinCC Unified Runtime app must be running .",
        "A project must be added as described in Add Project .",
    ]
    
    print("Testing your exact sentences:")
    for i, sentence in enumerate(user_sentences, 1):
        print(f"\nSentence {i}: '{sentence}'")
        
        results = check(sentence)
        punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ STILL FLAGGED: {len(punctuation_issues)} formatting issues")
            for issue in punctuation_issues:
                print(f"   - '{issue['text']}' - {issue['message']}")
        else:
            print(f"✅ SUCCESS: No longer flagged for space before punctuation!")
    
    # Test a regular sentence that should still be flagged
    print(f"\nTesting regular sentence (should still be flagged):")
    regular_sentence = "This is wrong . A regular sentence."
    print(f"Regular sentence: '{regular_sentence}'")
    
    results = check(regular_sentence)
    punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
    
    if punctuation_issues:
        print(f"✅ GOOD: Regular sentence still correctly flagged")
    else:
        print(f"❌ PROBLEM: Regular sentence should have been flagged")

if __name__ == "__main__":
    simple_final_test()
