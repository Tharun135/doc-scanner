#!/usr/bin/env python3
"""
Debug why can_may_terms rule isn't catching the original sentence
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.can_may_terms import check

def debug_can_may():
    """Debug the can_may_terms rule"""
    
    test_sentence = "You can configure an IEC 61850 data source in the Common Configurator."
    print(f"Testing: {test_sentence}")
    
    suggestions = check(test_sentence)
    print(f"Suggestions: {len(suggestions)}")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Test a simpler sentence
    simple_sentence = "You can do this."
    print(f"\nTesting simpler: {simple_sentence}")
    
    simple_suggestions = check(simple_sentence)
    print(f"Suggestions: {len(simple_suggestions)}")
    
    for i, suggestion in enumerate(simple_suggestions, 1):
        print(f"  {i}. {suggestion}")

if __name__ == "__main__":
    debug_can_may()
