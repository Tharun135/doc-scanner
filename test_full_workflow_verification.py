#!/usr/bin/env python3
"""Test the full application with our test document."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.app import review_document, load_rules, analyze_text
import json

def test_full_workflow():
    """Test the complete workflow with our test document."""
    
    # Create app instance
    app = create_app()
    
    # Read the test document
    with open('test_full_app.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("=== ANALYZING TEST DOCUMENT ===")
    print(f"Document text:\n{text[:200]}...\n")
    
    # Analyze the document
    with app.app_context():
        rules = load_rules()
        sentences = analyze_text(text)
        results = review_document(text, rules)
    
    print(f"=== ANALYSIS RESULTS ===")
    issues = results.get('issues', [])
    print(f"Found {len(issues)} issues:")
    
    for i, issue in enumerate(issues, 1):
        print(f"\n--- Issue {i} ---")
        if isinstance(issue, dict):
            print(f"Text: '{issue.get('text', '')}'")
            print(f"Message: {issue.get('message', '')}")
            if 'start' in issue and 'end' in issue:
                print(f"Position: {issue['start']}-{issue['end']}")
        else:
            print(f"Issue: {issue}")
    
    # Test AI suggestions for modal verb issues
    print(f"\n=== TESTING AI SUGGESTIONS ===")
    modal_verb_issues = [issue for issue in issues if isinstance(issue, dict) and 'may' in issue.get('text', '').lower()]
    
    for issue in modal_verb_issues:
        print(f"\nTesting AI suggestion for: '{issue.get('text', '')}'")
        
        # Import AI improvement function
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        # Get AI suggestion
        suggestion = get_enhanced_ai_suggestion(issue.get('message', ''), issue.get('text', ''))
        print(f"AI Suggestion: {suggestion}")

if __name__ == '__main__':
    test_full_workflow()
