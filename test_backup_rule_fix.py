#!/usr/bin/env python3
"""
Test the fixed backup rule to ensure it doesn't flag correct noun usage
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.rules.terminology_b_terms import check

def test_backup_rule_fix():
    """Test that the backup rule fix works correctly"""
    
    test_cases = [
        # Cases that should NOT be flagged (correct noun/adjective usage)
        {
            "text": "Both options support backup files from the server",
            "should_flag": False,
            "description": "Noun usage: backup files"
        },
        {
            "text": "The backup process takes several hours",
            "should_flag": False,
            "description": "Noun usage: backup process"
        },
        {
            "text": "Create a backup copy of the database",
            "should_flag": False,
            "description": "Adjective usage: backup copy"
        },
        {
            "text": "We provide backup and restore functionality",
            "should_flag": False,
            "description": "Noun usage: backup and restore"
        },
        {
            "text": "The system includes backup data protection",
            "should_flag": False,
            "description": "Adjective usage: backup data"
        },
        
        # Cases that SHOULD be flagged (incorrect verb usage)
        {
            "text": "Remember to backup your files regularly",
            "should_flag": True,
            "description": "Verb usage: to backup"
        },
        {
            "text": "You should backup your data weekly",
            "should_flag": True,
            "description": "Verb usage: should backup"
        },
        {
            "text": "Please backup the database before proceeding",
            "should_flag": True,
            "description": "Imperative verb usage: backup the database"
        },
        {
            "text": "Don't forget to backup all critical files",
            "should_flag": True,
            "description": "Verb usage: to backup"
        },
        {
            "text": "Backup your important documents regularly",
            "should_flag": True,
            "description": "Imperative verb usage at start"
        }
    ]
    
    print("=== Testing Backup Rule Fix ===")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['description']}")
        print(f"Text: '{test_case['text']}'")
        print(f"Should flag: {test_case['should_flag']}")
        
        # Check the rule
        suggestions = check(test_case['text'])
        backup_suggestions = [s for s in suggestions if 'back up' in s and 'verb' in s]
        is_flagged = len(backup_suggestions) > 0
        
        print(f"Result: {'Flagged' if is_flagged else 'Not flagged'}")
        if backup_suggestions:
            print(f"Suggestions: {backup_suggestions}")
        
        # Verify correctness
        if test_case['should_flag'] == is_flagged:
            print("✅ CORRECT")
        else:
            print("❌ INCORRECT - Rule needs adjustment")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_backup_rule_fix()
