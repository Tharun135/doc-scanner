#!/usr/bin/env python3
"""Test to debug the passive voice detection issue with "The"."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.rag_rule_helper import detect_passive_voice_issues

def test_passive_voice_debug():
    """Debug why "The" is being flagged as passive voice."""
    
    test_cases = [
        "The",
        "The document",
        "The document is written",
        "The document was written by John",
        "This is normal text",
        "The quick brown fox jumps"
    ]
    
    print("🐛 DEBUGGING PASSIVE VOICE DETECTION")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {repr(test_text)}")
        
        try:
            issues = detect_passive_voice_issues(test_text, test_text)
            print(f"   Found {len(issues)} issues:")
            
            for j, issue in enumerate(issues, 1):
                print(f"   Issue {j}:")
                print(f"     Text: {repr(issue['text'])}")
                print(f"     Position: {issue['start']}-{issue['end']}")
                print(f"     Message: {issue['message']}")
                print(f"     Context: {repr(issue['context'])}")
        except Exception as e:
            print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_passive_voice_debug()
