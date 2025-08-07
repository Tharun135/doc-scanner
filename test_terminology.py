#!/usr/bin/env python3
"""
Test script to verify custom terminology functionality.
"""

import sys
import os

# Add the app directory to the path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Test imports
try:
    from custom_terminology import get_terminology_manager, is_custom_whitelisted
    print("✓ Custom terminology imports successful")
except ImportError as e:
    print(f"✗ Custom terminology import failed: {e}")
    exit(1)

# Test spelling checker with custom terminology
try:
    sys.path.insert(0, os.path.join(app_dir, 'rules'))
    from spelling_checker import check
    print("✓ Spelling checker imports successful")
except ImportError as e:
    print(f"✗ Spelling checker import failed: {e}")
    exit(1)

def test_custom_terminology():
    """Test custom terminology functionality."""
    print("\n=== Testing Custom Terminology ===")
    
    # Get terminology manager
    manager = get_terminology_manager()
    print(f"Initial term count: {manager.get_terms_count()}")
    
    # Test if 'runtime' is whitelisted
    runtime_whitelisted = is_custom_whitelisted('runtime')
    print(f"'runtime' is whitelisted: {runtime_whitelisted}")
    
    # Test if 'Runtime' (capitalized) is whitelisted
    runtime_cap_whitelisted = is_custom_whitelisted('Runtime')
    print(f"'Runtime' is whitelisted: {runtime_cap_whitelisted}")
    
    # Add a test term
    test_term = "testruntime"
    added = manager.add_term(test_term)
    print(f"Added '{test_term}': {added}")
    
    # Check if it's now whitelisted
    test_whitelisted = is_custom_whitelisted(test_term)
    print(f"'{test_term}' is whitelisted: {test_whitelisted}")
    
    # Remove the test term
    removed = manager.remove_term(test_term)
    print(f"Removed '{test_term}': {removed}")
    
    # Test spelling checker with text containing 'runtime'
    print("\n=== Testing Spell Checker Integration ===")
    test_text = "The WinCC Unified Runtime app supports the configuration of industrial automation systems."
    suggestions = check(test_text)
    
    print(f"Test text: {test_text}")
    print(f"Spelling suggestions: {len(suggestions)}")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    else:
        print("  No spelling issues found (runtime should be whitelisted)")

if __name__ == "__main__":
    test_custom_terminology()
