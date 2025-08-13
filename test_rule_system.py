#!/usr/bin/env python3
"""
Test the actual rule system to debug why no issues are being detected.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual functions from app.py
from app.app import get_rules, analyze_sentence

def test_rule_system():
    print("🔧 Testing rule system...")
    
    # Test text with obvious issues
    test_text = "The document was written by the team. It should be reviewed carefully. This needs to be done quickly."
    
    print(f"📄 Test text: {test_text}")
    print()
    
    # Load rules
    print("📋 Loading rules...")
    rules = get_rules()
    print(f"✅ Loaded {len(rules)} rules")
    print()
    
    # Print rule details
    print("🔍 Rule details:")
    for i, rule in enumerate(rules):
        rule_name = getattr(rule, '__name__', f'rule_{i}')
        if hasattr(rule, '__module__'):
            module_name = rule.__module__
            if 'rules.' in module_name:
                rule_name = module_name.split('rules.')[-1]
        print(f"  {i+1}. {rule_name} (from {getattr(rule, '__module__', 'unknown')})")
    print()
    
    # Test each rule individually
    print("🧪 Testing each rule individually:")
    for i, rule in enumerate(rules):
        rule_name = getattr(rule, '__name__', f'rule_{i}')
        if hasattr(rule, '__module__'):
            module_name = rule.__module__
            if 'rules.' in module_name:
                rule_name = module_name.split('rules.')[-1]
        
        try:
            result = rule(test_text)
            if result:
                print(f"  ✅ {rule_name}: Found {len(result) if isinstance(result, list) else 1} issues")
                if isinstance(result, list):
                    for issue in result:
                        print(f"     - {issue}")
                else:
                    print(f"     - {result}")
            else:
                print(f"  ➖ {rule_name}: No issues found")
        except Exception as e:
            print(f"  ❌ {rule_name}: Error - {e}")
    print()
    
    # Test full sentence analysis
    print("🔍 Testing full sentence analysis:")
    feedback, readability_scores, quality_score = analyze_sentence(test_text, rules)
    
    print(f"📊 Results:")
    print(f"  - Issues found: {len(feedback)}")
    print(f"  - Quality score: {quality_score}")
    print(f"  - Readability scores: {readability_scores}")
    
    if feedback:
        print("  - Issues details:")
        for issue in feedback:
            print(f"     {issue}")
    else:
        print("  - No issues detected")

if __name__ == "__main__":
    test_rule_system()
