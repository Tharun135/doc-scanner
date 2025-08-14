#!/usr/bin/env python3
"""Test the passive voice fix for short sentences."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.rag_rule_helper import detect_passive_voice_issues

def test_passive_voice_fix():
    """Test that very short sentences are filtered out."""
    
    test_cases = [
        ("The", "Should be filtered out - too short"),
        ("It is", "Should be filtered out - too short"), 
        ("Is done", "Should be filtered out - too short"),
        ("The task is done", "Should be detected - long enough"),
        ("The document is written", "Should be detected - long enough"),
        ("This was made by John", "Should be detected - long enough")
    ]
    
    print("🔧 TESTING PASSIVE VOICE FIX")
    print("=" * 50)
    
    for i, (test_text, expected) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {repr(test_text)}")
        print(f"   Expected: {expected}")
        
        try:
            issues = detect_passive_voice_issues(test_text, test_text)
            print(f"   Found {len(issues)} issues:")
            
            for j, issue in enumerate(issues, 1):
                print(f"   Issue {j}:")
                print(f"     Text: {repr(issue['text'])}")
                print(f"     Context: {repr(issue['context'])}")
                print(f"     Message: {issue['message']}")
                
        except Exception as e:
            print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_passive_voice_fix()
