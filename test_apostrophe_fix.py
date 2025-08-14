#!/usr/bin/env python3
"""
Test script to verify apostrophe handling in quotation mark rule
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.punctuation_rules import check_quotation_marks

def test_apostrophe_handling():
    """Test that apostrophes don't trigger quotation mark warnings"""
    
    test_cases = [
        {
            "text": "Don't worry about it",
            "should_trigger": False,
            "description": "Single apostrophe in contraction"
        },
        {
            "text": "John's car is red",
            "should_trigger": False,
            "description": "Possessive apostrophe"
        },
        {
            "text": "I can't believe it's working",
            "should_trigger": False,
            "description": "Multiple apostrophes in contractions"
        },
        {
            "text": "He said 'hello' to me",
            "should_trigger": False,
            "description": "Proper paired single quotes"
        },
        {
            "text": "She said 'hello and left",
            "should_trigger": True,
            "description": "Unmatched single quotation mark"
        },
        {
            "text": "Don't use 'improper quotes",
            "should_trigger": True,
            "description": "Apostrophe + unmatched quote"
        }
    ]
    
    print("🧪 Testing apostrophe handling in quotation mark rule...")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        should_trigger = test_case["should_trigger"]
        description = test_case["description"]
        
        # Run the check
        issues = check_quotation_marks(text)
        
        # Filter for single quote issues only
        single_quote_issues = [issue for issue in issues if "single quotation" in issue.get("message", "")]
        
        has_issue = len(single_quote_issues) > 0
        
        print(f"Test {i}: {description}")
        print(f"  Text: \"{text}\"")
        print(f"  Expected issue: {should_trigger}")
        print(f"  Actual issue: {has_issue}")
        
        if has_issue == should_trigger:
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL")
            all_passed = False
            if has_issue:
                print(f"     Issue detected: {single_quote_issues[0]['message']}")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Apostrophe handling is working correctly.")
    else:
        print("❌ Some tests failed. Check the logic above.")
    
    return all_passed

if __name__ == "__main__":
    test_apostrophe_handling()
