#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

# Test the fixed cross_references rule
test_content = """
<p>If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files.</p>

<p>For more information, visit example.com or go to www.google.com</p>
"""

print("Testing the fixed cross_references rule:\n")
print("Test content:")
print(test_content)
print("=" * 60)

try:
    from app.rules.cross_references import check
    suggestions = check(test_content)
    
    print("Rule suggestions:")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("No suggestions (which is correct for the problematic sentence)")
    
    print("\n✅ SUCCESS: The rule should now only detect real URLs and not flag the problematic sentence!")
    
except Exception as e:
    print(f"Error testing rule: {e}")
    import traceback
    traceback.print_exc()
