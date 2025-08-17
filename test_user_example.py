#!/usr/bin/env python3
"""
Test with the user's specific example
"""

from app.rules.formatting_fixed import check

def test_user_example():
    print("=== TESTING USER'S SPECIFIC EXAMPLE ===\n")
    
    user_text = """Prerequisite
The WinCC Unified Runtime app must be running.
A project must be added as described in Add Project."""
    
    print(f"Original text:")
    print(repr(user_text))
    print()
    print("Formatted text:")
    print(user_text)
    print()
    
    results = check(user_text)
    print(f"Total issues found: {len(results)}")
    
    punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
    if punctuation_issues:
        print(f"❌ Punctuation spacing issues: {len(punctuation_issues)}")
        for issue in punctuation_issues:
            print(f"   - '{issue['text']}' at {issue['start']}-{issue['end']}")
    else:
        print(f"✅ No punctuation spacing issues found!")
    
    # Show other issues
    other_issues = [r for r in results if "space before punctuation" not in r.get('message', '')]
    if other_issues:
        print(f"\nOther formatting issues: {len(other_issues)}")
        for issue in other_issues:
            print(f"   - {issue['message']}: '{issue['text']}' at {issue['start']}-{issue['end']}")

    # Test with list format
    print("\n" + "="*50)
    print("TESTING WITH LIST FORMAT:")
    
    list_text = """Prerequisite:
- The WinCC Unified Runtime app must be running.
- A project must be added as described in Add Project."""
    
    print(f"List formatted text:")
    print(list_text)
    print()
    
    results = check(list_text)
    punctuation_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
    if punctuation_issues:
        print(f"❌ Punctuation spacing issues: {len(punctuation_issues)}")
        for issue in punctuation_issues:
            print(f"   - '{issue['text']}' at {issue['start']}-{issue['end']}")
    else:
        print(f"✅ No punctuation spacing issues found!")

if __name__ == "__main__":
    test_user_example()
