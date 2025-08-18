#!/usr/bin/env python3
"""
Simple test to verify spelling checker with runtime.
"""

import sys
import os

# Add app directory to path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
sys.path.insert(0, app_dir)

try:
    # Import and test custom terminology
    from custom_terminology import get_terminology_manager, is_custom_whitelisted
    print("✓ Custom terminology imports successful")
    
    # Get manager and check runtime
    manager = get_terminology_manager()
    print(f"Custom terms loaded: {manager.get_terms_count()}")
    
    # Check if runtime is whitelisted
    is_runtime_whitelisted = is_custom_whitelisted('runtime')
    print(f"'runtime' is whitelisted: {is_runtime_whitelisted}")
    
    # Test spelling checker
    sys.path.insert(0, os.path.join(app_dir, 'rules'))
    from spelling_checker import check
    print("✓ Spelling checker imports successful")
    
    # Test text with runtime
    test_text = "The WinCC Unified Runtime app supports the configuration."
    suggestions = check(test_text)
    print(f"\nTest text: {test_text}")
    print(f"Spelling suggestions: {len(suggestions)}")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("  ✓ No spelling issues found - runtime should be whitelisted")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
