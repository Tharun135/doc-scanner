#!/usr/bin/env python3
"""
Test the updated spelling checker with runtime support.
"""

import sys
import os

# Add paths
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
rules_dir = os.path.join(app_dir, 'rules')
sys.path.insert(0, app_dir)
sys.path.insert(0, rules_dir)

try:
    from simple_terminology import is_custom_whitelisted
    print("✓ Simple terminology imports successful")
    
    # Test runtime
    is_runtime_whitelisted = is_custom_whitelisted('runtime')
    print(f"'runtime' is whitelisted: {is_runtime_whitelisted}")
    
    # Test spelling checker
    from spelling_checker import check
    print("✓ Spelling checker imports successful")
    
    # Test text with runtime
    test_texts = [
        "The WinCC Unified Runtime app supports the configuration.",
        "Runtime error in the system.",
        "The runtyme is incorrect.",  # Misspelling
        "This sentance has mispelled words."  # Other misspellings
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {test_text}")
        suggestions = check(test_text)
        print(f"Spelling suggestions: {len(suggestions)}")
        for j, suggestion in enumerate(suggestions, 1):
            print(f"  {j}. {suggestion}")
        if not suggestions:
            print("  ✓ No spelling issues found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
