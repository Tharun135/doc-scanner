#!/usr/bin/env python3
"""
Test web app analysis exactly like the web interface does.
"""

import sys
import os
sys.path.append('.')

from app.app import analyze_sentence, get_rules

def test_web_analysis():
    """Test web app analysis exactly like the web interface does."""
    
    # Test text with obvious issues
    test_text = 'The document was written by the team and the system was configured by the admin.'
    print('=== TESTING WEB APP EXACTLY LIKE WEB INTERFACE ===')
    print(f'Text: {test_text}')
    
    try:
        # Load rules (like web app does)
        rules = get_rules()
        print(f'Loaded {len(rules)} rules')
        
        # Analyze sentence (exactly like web app does)
        feedback, readability_scores, quality_score = analyze_sentence(test_text, rules)
        
        print(f'Number of issues: {len(feedback)}')
        print(f'Quality score: {quality_score}')
        
        if feedback:
            print('Issues found:')
            for i, issue in enumerate(feedback, 1):
                print(f'{i}. {issue}')
        else:
            print('No issues found!')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_web_analysis()
