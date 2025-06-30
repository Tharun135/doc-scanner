#!/usr/bin/env python3
"""
Simple test to verify rules are integrated into the main app.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.rules import rule_functions
    print(f"✅ Successfully loaded {len(rule_functions)} rules")
    
    # Test a few rules with specific text
    test_text = "This is is a well known issue with supporteds features."
    
    print(f"\nTesting with: '{test_text}'")
    
    issues_found = 0
    for i, rule_func in enumerate(rule_functions):
        try:
            result = rule_func(test_text)
            if result:  # If rule found issues
                issues_found += len(result)
                print(f"Rule {i+1}: Found {len(result)} issue(s)")
                for issue in result[:1]:  # Show first issue only
                    print(f"  - {issue[:80]}...")
        except Exception as e:
            print(f"Rule {i+1}: Error - {e}")
    
    print(f"\nTotal issues found across all rules: {issues_found}")
    
    # Test specifically our new rules
    print("\n" + "="*50)
    print("Testing New Rules Specifically")
    print("="*50)
    
    # Test the last 3 rules (should be our new ones)
    new_rule_tests = [
        ("Repeated words", "This is is a test sentence."),
        ("Incorrect verbs", "The feature is supporteds by the system."),
        ("Grammar issues", "This is a well known feature.")
    ]
    
    for i, (test_name, test_text) in enumerate(new_rule_tests):
        rule_index = -(3-i)  # -3, -2, -1
        try:
            result = rule_functions[rule_index](test_text)
            print(f"\n{test_name}: {len(result) if result else 0} issues")
            if result:
                print(f"  {result[0]}")
        except Exception as e:
            print(f"\n{test_name}: Error - {e}")
    
except ImportError as e:
    print(f"❌ Failed to import rules: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
