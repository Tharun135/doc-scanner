#!/usr/bin/env python3
"""
Simple test for the grammar issues rule.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_compound_adjectives():
    """Test compound adjective detection."""
    print("Testing compound adjective detection...")
    
    try:
        from rules.grammar_issues import check
        
        # Your specific example
        test_sentence = "You need this tool to convert vendor and device specific configuration files to the standardized Connectivity-Suite compatible configurations."
        
        print(f"Testing: {test_sentence}")
        
        suggestions = check(test_sentence)
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. {suggestion}")
        else:
            print("No issues detected.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_compound_adjectives()
