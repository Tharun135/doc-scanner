#!/usr/bin/env python3
"""
Simple test for apostrophe rule
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.rules.special_characters import check
    
    # Simple test
    test_text = "Tharun's laptop is working."
    print(f"Testing: {test_text}")
    
    result = check(test_text)
    print(f"Result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
