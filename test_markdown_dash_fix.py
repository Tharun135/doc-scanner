#!/usr/bin/env python3
"""
Test script to verify markdown table syntax handling in dash usage rule
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.punctuation_rules import check_dash_usage

def test_markdown_table_handling():
    """Test that markdown table syntax doesn't trigger dash usage warnings"""
    
    test_cases = [
        {
            "text": """| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |""",
            "should_trigger": False,
            "description": "Markdown table with dashes"
        },
        {
            "text": """| Name | Age | City |
| --- | --- | --- |
| John | 25 | NYC |""",
            "should_trigger": False,
            "description": "Markdown table with short dashes"
        },
        {
            "text": """---
title: Document
author: User
---""",
            "should_trigger": False,
            "description": "YAML front matter"
        },
        {
            "text": "---",
            "should_trigger": False,
            "description": "Horizontal rule"
        },
        {
            "text": "This is a sentence -- and this should be an em-dash.",
            "should_trigger": True,
            "description": "Genuine em-dash case"
        },
        {
            "text": "Code example: function() { return value--; }",
            "should_trigger": False,
            "description": "Code-like content"
        },
        {
            "text": "URL: https://example.com/page--name",
            "should_trigger": False,
            "description": "URL with double hyphen"
        },
        {
            "text": "He said -- quite emphatically -- that it worked.",
            "should_trigger": True,
            "description": "Parenthetical expression with double hyphen"
        }
    ]
    
    print("🧪 Testing markdown table handling in dash usage rule...")
    print("=" * 70)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        should_trigger = test_case["should_trigger"]
        description = test_case["description"]
        
        # Run the check
        issues = check_dash_usage(text)
        
        # Filter for em-dash issues
        em_dash_issues = [issue for issue in issues if "em-dash" in issue.get("message", "")]
        
        has_issue = len(em_dash_issues) > 0
        
        print(f"Test {i}: {description}")
        print(f"  Text: {repr(text[:100])}")
        print(f"  Expected issue: {should_trigger}")
        print(f"  Actual issue: {has_issue}")
        
        if has_issue == should_trigger:
            print(f"  ✅ PASS")
        else:
            print(f"  ❌ FAIL")
            all_passed = False
            if has_issue:
                print(f"     Issue detected: {em_dash_issues[0]['message']}")
        
        print()
    
    print("=" * 70)
    if all_passed:
        print("🎉 All tests passed! Markdown table syntax is properly handled.")
    else:
        print("❌ Some tests failed. Check the logic above.")
    
    return all_passed

if __name__ == "__main__":
    test_markdown_table_handling()
