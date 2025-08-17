#!/usr/bin/env python3
"""Test the modified punctuation rule to ensure it excludes titles"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.punctuation_fixed import check

def test_punctuation_rule():
    print("🧪 TESTING MODIFIED PUNCTUATION RULE")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "text": "Introduction",
            "description": "Simple title (should be excluded)",
            "should_flag": False
        },
        {
            "text": "Chapter 1: Getting Started",
            "description": "Chapter title (should be excluded)",
            "should_flag": False
        },
        {
            "text": "Table of Contents",
            "description": "Common title (should be excluded)",
            "should_flag": False
        },
        {
            "text": "This is a regular sentence without punctuation",
            "description": "Regular sentence (should be flagged)",
            "should_flag": True
        },
        {
            "text": "This is a proper sentence.",
            "description": "Proper sentence with punctuation (should not be flagged)",
            "should_flag": False
        },
        {
            "text": "Project Management Overview",
            "description": "Title case heading (should be excluded)",
            "should_flag": False
        },
        {
            "text": "the quick brown fox jumps over the lazy dog",
            "description": "Lowercase sentence (should be flagged)",
            "should_flag": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Text: '{test_case['text']}'")
        
        issues = check(test_case['text'])
        punctuation_issues = [issue for issue in issues if "missing ending punctuation" in issue['message']]
        
        was_flagged = len(punctuation_issues) > 0
        expected = test_case['should_flag']
        
        if was_flagged == expected:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"Expected: {'Flag' if expected else 'No flag'}")
        print(f"Result: {'Flagged' if was_flagged else 'Not flagged'}")
        print(f"Status: {status}")
        
        if punctuation_issues:
            print(f"Issues found: {len(punctuation_issues)}")
            for issue in punctuation_issues:
                print(f"  - {issue['message']}")

if __name__ == "__main__":
    test_punctuation_rule()
