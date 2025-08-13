#!/usr/bin/env python3
"""
Rule Detection Debug Script
Test all rules to see which ones are working
"""

import sys
sys.path.append('app')

from app.app import get_rules, review_document

def test_all_rules():
    """Test which rules are actually working"""
    
    print("🔍 Testing rule detection...")
    
    # Get all rules
    rules = get_rules()
    print(f"Total rules loaded: {len(rules)}")
    
    # Print first few rules to see what we have
    print(f"\nFirst 10 rules:")
    for i, rule in enumerate(rules[:10]):
        print(f"  {i+1}. {rule}")
    
    # Test content that should trigger multiple rules
    test_content = """This document contains many writing issues that should be detected. The passive voice was used extensively throughout this document. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it difficult for readers to follow the main point and becomes extremely verbose and complex. Additionally, the document utilizes verbose language patterns that could be simplified. Furthermore, complex terminology was implemented to demonstrate detection capabilities. Very important information is provided here. The documentation is very comprehensive and very detailed."""
    
    print(f"\nTest content length: {len(test_content)} characters")
    print(f"Test content: {test_content[:200]}...")
    
    # Test direct rule processing
    print(f"\n🔧 Testing review_document function...")
    result = review_document(test_content, rules)
    
    print(f"review_document result type: {type(result)}")
    print(f"review_document result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if isinstance(result, dict) and 'issues' in result:
        issues = result['issues']
        print(f"Number of issues found: {len(issues)}")
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            if isinstance(issue, dict) and 'message' in issue:
                message = issue['message'].lower()
                if 'passive voice' in message:
                    issue_types.setdefault('Passive Voice', []).append(issue)
                elif 'long sentence' in message:
                    issue_types.setdefault('Long Sentence', []).append(issue)
                elif 'very' in message and 'modifier' in message:
                    issue_types.setdefault('Unnecessary Modifiers', []).append(issue)
                elif 'verbose' in message:
                    issue_types.setdefault('Verbose Language', []).append(issue)
                elif 'utilize' in message or 'simplif' in message:
                    issue_types.setdefault('Word Choice', []).append(issue)
                else:
                    issue_types.setdefault('Other', []).append(issue)
            else:
                issue_types.setdefault('Invalid Format', []).append(str(issue))
        
        print(f"\nIssues by type:")
        for issue_type, issues in issue_types.items():
            print(f"  {issue_type}: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3 of each type
                if isinstance(issue, dict):
                    print(f"    - {issue.get('message', str(issue))[:100]}...")
                else:
                    print(f"    - {str(issue)[:100]}...")
    else:
        print(f"Unexpected result format: {result}")
    
    # Test individual rule types
    print(f"\n🔧 Testing specific rules...")
    
    # Test passive voice
    passive_test = "The document was written by the author."
    print(f"Passive voice test: '{passive_test}'")
    passive_result = review_document(passive_test, rules)
    if isinstance(passive_result, dict) and 'issues' in passive_result:
        print(f"  Result: {len(passive_result['issues'])} issues")
        if passive_result['issues']:
            print(f"  First issue: {passive_result['issues'][0].get('message', 'No message')}")
    
    # Test long sentence
    long_test = "This is an extremely long sentence that continues to go on and on without any clear purpose or direction, making it very difficult for readers to follow the main point and understand what the author is trying to communicate to them."
    print(f"Long sentence test: '{long_test[:60]}...'")
    long_result = review_document(long_test, rules)
    if isinstance(long_result, dict) and 'issues' in long_result:
        print(f"  Result: {len(long_result['issues'])} issues")
        if long_result['issues']:
            print(f"  First issue: {long_result['issues'][0].get('message', 'No message')}")
    
    # Test verbose language
    verbose_test = "The document utilizes comprehensive methodologies to facilitate understanding."
    print(f"Verbose language test: '{verbose_test}'")
    verbose_result = review_document(verbose_test, rules)
    if isinstance(verbose_result, dict) and 'issues' in verbose_result:
        print(f"  Result: {len(verbose_result['issues'])} issues")
        if verbose_result['issues']:
            print(f"  First issue: {verbose_result['issues'][0].get('message', 'No message')}")
    
    # Test unnecessary modifiers
    modifier_test = "This is a very important and very comprehensive document with very detailed information."
    print(f"Modifier test: '{modifier_test}'")
    modifier_result = review_document(modifier_test, rules)
    if isinstance(modifier_result, dict) and 'issues' in modifier_result:
        print(f"  Result: {len(modifier_result['issues'])} issues")
        if modifier_result['issues']:
            print(f"  First issue: {modifier_result['issues'][0].get('message', 'No message')}")

def test_smart_filter():
    """Test if SmartRAGManager is filtering out rules"""
    try:
        from app.smart_rule_filter import SmartRAGManager
        
        print(f"\n🔧 Testing SmartRAGManager...")
        
        # Check if it's in performance mode
        smart_manager = SmartRAGManager()
        print(f"SmartRAGManager initialized")
        
        # Test content
        test_content = "This document utilizes very comprehensive methodologies."
        
        # Get all rules first
        all_rules = get_rules()
        print(f"All rules count: {len(all_rules)}")
        
        # Test with SmartRAGManager
        filtered_rules = smart_manager.get_relevant_rules(test_content, all_rules)
        print(f"Filtered rules count: {len(filtered_rules)}")
        
        print(f"Rules being filtered out: {len(all_rules) - len(filtered_rules)}")
        
        if len(filtered_rules) < len(all_rules):
            print("⚠️  SmartRAGManager is filtering out rules!")
            print("This might be why you're only seeing passive voice and long sentences.")
            
            # Show which rules are being kept
            print(f"\nFiltered rules (first 10):")
            for i, rule in enumerate(filtered_rules[:10]):
                print(f"  {i+1}. {rule}")
        
    except Exception as e:
        print(f"SmartRAGManager test error: {str(e)}")

if __name__ == "__main__":
    test_all_rules()
    test_smart_filter()
