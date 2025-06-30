#!/usr/bin/env python3
"""
Test script to verify all new grammar rules are integrated and working properly.
This tests the complete integration including the __init__.py file updates.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules import rule_functions
from app.rules.repeated_words import check as check_repeated_words
from app.rules.incorrect_verb_forms import check as check_incorrect_verb_forms
from app.rules.grammar_issues import check as check_grammar_issues

def test_rule_integration():
    """Test that all new rules are integrated into the rule_functions list."""
    print("Testing rule integration...")
    
    # Check that all our new rules are in the rule_functions list
    rule_names = [func.__name__ for func in rule_functions]
    
    expected_new_rules = ['check_repeated_words', 'check_incorrect_verb_forms', 'check_grammar_issues']
    
    print(f"Total rules loaded: {len(rule_functions)}")
    print(f"Rule functions available: {len(rule_names)}")
    
    for expected_rule in expected_new_rules:
        if expected_rule in rule_names:
            print(f"✅ {expected_rule} is integrated")
        else:
            print(f"❌ {expected_rule} is NOT integrated")
    
    print("\nAll rule names:")
    for i, name in enumerate(sorted(rule_names), 1):
        print(f"{i:2d}. {name}")

def test_repeated_words():
    """Test the repeated words rule."""
    print("\n" + "="*50)
    print("Testing Repeated Words Rule")
    print("="*50)
    
    test_cases = [
        "This is is a test sentence.",
        "The the quick brown fox jumps.",
        "I can can see the issue clearly.",
        "Please check check this document.",
        "This is a normal sentence."
    ]
    
    for text in test_cases:
        print(f"\nText: '{text}'")
        issues = check_repeated_words(text)
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  No issues found")

def test_incorrect_verb_forms():
    """Test the incorrect verb forms rule."""
    print("\n" + "="*50)
    print("Testing Incorrect Verb Forms Rule")
    print("="*50)
    
    test_cases = [
        "The feature is supporteds by the system.",
        "This option is createds automatically.", 
        "The data is processeds correctly.",
        "Users are logineds to the system.",
        "This is a normal supported feature."
    ]
    
    for text in test_cases:
        print(f"\nText: '{text}'")
        issues = check_incorrect_verb_forms(text)
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  No issues found")

def test_grammar_issues():
    """Test the grammar issues rule."""
    print("\n" + "="*50)
    print("Testing Grammar Issues Rule")
    print("="*50)
    
    test_cases = [
        "This is a well known feature.",
        "A state of the art solution.",
        "The long term effects are positive.",
        "They was going to the store.",
        "Each of the students have their books.",
        "This is a normal sentence."
    ]
    
    for text in test_cases:
        print(f"\nText: '{text}'")
        issues = check_grammar_issues(text)
        if issues:
            for issue in issues:
                print(f"  {issue}")
        else:
            print("  No issues found")

def test_combined_scenario():
    """Test a text with multiple types of issues."""
    print("\n" + "="*50)
    print("Testing Combined Scenario")
    print("="*50)
    
    text = """
    This is is a well known issue with supporteds features. 
    The the long term solution was was implemented correctly.
    Each user have have their own settings that is createds automatically.
    """
    
    print(f"Text: {text.strip()}")
    
    all_issues = []
    
    # Test each rule
    repeated_issues = check_repeated_words(text)
    verb_issues = check_incorrect_verb_forms(text)
    grammar_issues_list = check_grammar_issues(text)
    
    all_issues.extend(repeated_issues)
    all_issues.extend(verb_issues)
    all_issues.extend(grammar_issues_list)
    
    print(f"\nTotal issues found: {len(all_issues)}")
    
    for i, issue in enumerate(all_issues, 1):
        print(f"\n{i}. {issue}")

if __name__ == "__main__":
    print("Doc Scanner - New Grammar Rules Integration Test")
    print("=" * 60)
    
    test_rule_integration()
    test_repeated_words()
    test_incorrect_verb_forms()
    test_grammar_issues()
    test_combined_scenario()
    
    print("\n" + "="*60)
    print("Integration test complete!")
