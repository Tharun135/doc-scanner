#!/usr/bin/env python3
"""
Test the specific sentences provided by the user
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.grammar_rules import check

def test_user_sentences():
    """Test the specific sentences provided by the user"""
    
    sentences = [
        "vals: data points published in the payload.",
        "id: unique identification of data point. You must fetch the tag ID from metadata payload based on the tag name.",
        "qc: quality code. It provides specific integer value to indicate the quality of the data point value.",
        "ts: timestamp of the data point. it is in ISO 8601 Zulu format.",
        "val: value of the Tag. Based on the data type of the data point, the value can be simple scalar value, an array, or an object."
    ]
    
    print("Testing user-provided sentences...")
    print("=" * 60)
    
    issues_found = False
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\n{i}. Testing: '{sentence}'")
        suggestions = check(sentence)
        capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
        
        if capital_suggestions:
            print("❌ ISSUE: This sentence would be flagged for capitalization!")
            for suggestion in capital_suggestions:
                print(f"   - {suggestion}")
            issues_found = True
        else:
            print("✅ GOOD: No capitalization issues flagged")
    
    print("\n" + "=" * 60)
    if issues_found:
        print("❌ PROBLEMS FOUND: Some sentences would still be incorrectly flagged")
        print("The rule needs further refinement to handle these cases.")
    else:
        print("✅ ALL GOOD: None of these sentences would be flagged")
    
    return not issues_found

if __name__ == "__main__":
    test_user_sentences()
