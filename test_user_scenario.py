#!/usr/bin/env python3
"""
Test the specific user scenario with colons
"""

from app.rules.punctuation_fixed import check

def test_user_scenario():
    print("=== TESTING USER'S SPECIFIC SCENARIO ===\n")
    
    # The user's scenario - document with headings ending in colons
    test_content = """Prerequisite:
The WinCC Unified Runtime app must be running.
A project must be added as described in Add Project.

Requirements:
The system must be configured properly.
All dependencies must be installed.

Steps:
Open the application.
Configure the settings."""

    print("Full document test:")
    print("=" * 50)
    print(test_content)
    print("=" * 50)
    
    results = check(test_content)
    punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
    
    print(f"\nTotal punctuation issues found: {len(results)}")
    print(f"Missing ending punctuation issues: {len(punctuation_issues)}")
    
    if punctuation_issues:
        print("\n❌ Issues with missing ending punctuation:")
        for i, issue in enumerate(punctuation_issues, 1):
            print(f"{i}. '{issue['text']}' - {issue['message']}")
    else:
        print("\n✅ No missing ending punctuation issues found!")
    
    # Test individual lines
    print(f"\n{'='*50}")
    print("INDIVIDUAL LINE TESTS:")
    print(f"{'='*50}")
    
    lines = test_content.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():  # Skip empty lines
            print(f"\nLine {i}: '{line}'")
            results = check(line)
            punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
            
            if punctuation_issues:
                print(f"❌ Missing punctuation issues: {len(punctuation_issues)}")
                for issue in punctuation_issues:
                    print(f"   - '{issue['text']}'")
            else:
                print(f"✅ No missing punctuation issues")

def test_colon_specific():
    print(f"\n{'='*60}")
    print("COLON-SPECIFIC TESTS:")
    print(f"{'='*60}")
    
    colon_tests = [
        "Prerequisite:",
        "Requirements:",
        "Note:",
        "Important:",
        "Configuration:",
        "The following steps are required:",
        "Please note the following:",
    ]
    
    for test in colon_tests:
        results = check(test)
        punctuation_issues = [r for r in results if "missing ending punctuation" in r.get('message', '')]
        
        if punctuation_issues:
            print(f"❌ '{test}' - INCORRECTLY flagged")
        else:
            print(f"✅ '{test}' - Correctly allowed")

if __name__ == "__main__":
    test_user_scenario()
    test_colon_specific()
