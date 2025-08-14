#!/usr/bin/env python3
"""Test the actual passive voice rule that's being used."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.passive_voice import check

def test_passive_voice_rule():
    """Test the main passive voice rule function."""
    
    test_cases = [
        "The",
        "The document", 
        "The document is written",
        "This is normal text",
        "The quick brown fox jumps"
    ]
    
    print("🔍 TESTING PASSIVE VOICE RULE")
    print("=" * 40)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {repr(test_text)}")
        
        try:
            issues = check(test_text)
            print(f"   Found {len(issues)} issues:")
            
            for j, issue in enumerate(issues, 1):
                print(f"   Issue {j}:")
                print(f"     Text: {repr(issue.get('text', 'N/A'))}")
                print(f"     Message: {issue.get('message', 'N/A')}")
                print(f"     Start: {issue.get('start', 'N/A')}")
                print(f"     End: {issue.get('end', 'N/A')}")
                if 'context' in issue:
                    print(f"     Context: {repr(issue['context'])}")
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_passive_voice_rule()
