#!/usr/bin/env python3
"""
Test a text with multiple obvious issues to see which rules detect them.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the actual functions from app.py
from app.app import get_rules, analyze_sentence

def test_obvious_issues():
    print("🔧 Testing text with multiple obvious issues...")
    
    # Test text with multiple obvious issues
    test_text = """The document was written by the team, and it should be reviewed carefully by management, and this process needs to be done quickly because there are many deadlines that were set by the project coordinators. The system can be configured by clicking on the settings button, and passwords should be changed regularly by users for better security purposes."""
    
    print(f"📄 Test text: {test_text}")
    print()
    
    # Load rules
    print("📋 Loading rules...")
    rules = get_rules()
    print(f"✅ Loaded {len(rules)} rules")
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
        for i, issue in enumerate(feedback, 1):
            print(f"     {i}. {issue}")
    else:
        print("  - No issues detected")
    
    print()
    print("🎯 Analysis complete!")

if __name__ == "__main__":
    test_obvious_issues()
