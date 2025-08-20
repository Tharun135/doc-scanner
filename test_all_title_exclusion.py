#!/usr/bin/env python3
"""
Quick test to verify title exclusion status across all rules
"""

import sys
import os
sys.path.append('.')

def test_all_rules_title_exclusion():
    from app.app import load_rules
    
    # Load all rules
    rules = load_rules()
    print(f"📊 Testing title exclusion with all {len(rules)} rules")
    
    # Test document with titles and regular content
    test_doc = '''
    <h1>User Documentation</h1>
    <h2>Getting Started Guide</h2>
    <p>Introduction</p>
    <p>INSTALLATION REQUIREMENTS</p>
    <p>1. Basic Configuration</p>
    
    <p>This regular sentence has several vague things that were written by someone and contains nominalizations like implementation.</p>
    '''
    
    total_issues = 0
    for i, rule in enumerate(rules, 1):
        rule_name = rule.__module__.split('.')[-1]
        try:
            suggestions = rule(test_doc)
            issue_count = len(suggestions) if suggestions else 0
            total_issues += issue_count
            print(f"{i:2d}. {rule_name.ljust(20)} - {issue_count} issues")
            if issue_count > 0 and suggestions:
                for suggestion in suggestions[:2]:  # Show first 2
                    print(f"    • {suggestion[:60]}...")
        except Exception as e:
            print(f"{i:2d}. {rule_name.ljust(20)} - ERROR: {str(e)[:50]}...")
    
    print(f"\n📊 Total issues found: {total_issues}")
    print("✅ Expected: Only regular sentence issues, no title issues")

if __name__ == "__main__":
    test_all_rules_title_exclusion()
