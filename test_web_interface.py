#!/usr/bin/env python3
"""
Test the web interface functionality to see why issues aren't being detected.
"""

import sys
import os
sys.path.append('.')

from app.app import analyze_sentence, get_rules

def test_web_interface_logic():
    """Test the same logic the web interface uses."""
    
    # Test text with obvious issues
    test_text = "The document was written by the team and the system was configured by the admin. This is a very long sentence that contains many words and clauses and should definitely be detected as being too long for good readability and user comprehension."
    
    print("=== TESTING WEB INTERFACE LOGIC ===")
    print(f"Text: {test_text}")
    print()
    
    try:
        # Load rules the same way the web interface does
        print("Loading rules...")
        rules = get_rules()
        print(f"Loaded {len(rules)} rules")
        print()
        
        # This is the function the web interface actually calls
        feedback, readability_scores, quality_score = analyze_sentence(test_text, rules)
        
        print(f"Feedback type: {type(feedback)}")
        print(f"Number of issues found: {len(feedback)}")
        print(f"Quality score: {quality_score}")
        print(f"Readability scores: {readability_scores}")
        print()
        
        if feedback:
            print("Issues found:")
            for i, issue in enumerate(feedback, 1):
                print(f"{i}. {issue}")
        else:
            print("No issues found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_interface_logic()
