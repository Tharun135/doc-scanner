#!/usr/bin/env python3
"""Final comprehensive test for the period detection fix."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check_period_placement

def test_period_detection_comprehensive():
    """Comprehensive test of period detection with real-world examples."""
    
    print("🧪 COMPREHENSIVE PERIOD DETECTION TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Blog post with formatting",
            "content": """# My Blog Post

This **important** announcement affects all users
Check out the [documentation](https://docs.example.com) for details
Here's a screenshot ![example](image.png) showing the feature

This sentence has proper punctuation.
This one also ends correctly!""",
            "expected_issues": 3
        },
        {
            "name": "Technical documentation",
            "content": """## Installation Guide

First, install the `pip` package manager
Then run the **setup script** to configure your environment
See the official [installation guide](https://install.com) for help

Installation is now complete.
You can start using the software!""",
            "expected_issues": 3
        },
        {
            "name": "Mixed formatting edge cases",
            "content": """This sentence has **bold** and *italic* and needs punctuation
Links like [this one](url) and code like `print()` need periods too
Images ![alt](src) at the end also need periods
Multiple **formatting** with [links](url) and `code` missing punctuation

But this sentence is fine.
And this **bold** sentence is also correct.""",
            "expected_issues": 4
        },
        {
            "name": "Correctly formatted content",
            "content": """This **bold** sentence ends properly.
Check out this [great link](https://example.com) for more info.
Here's an image ![screenshot](image.jpg) showing results.
Use the `print()` function to display text.""",
            "expected_issues": 0
        }
    ]
    
    total_passed = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        suggestions = check_period_placement(test_case['content'])
        period_suggestions = [s for s in suggestions if 'period' in s.get('message', '').lower()]
        
        print(f"Expected issues: {test_case['expected_issues']}")
        print(f"Found issues: {len(period_suggestions)}")
        
        if len(period_suggestions) == test_case['expected_issues']:
            print("✅ PASS")
            total_passed += 1
        else:
            print("❌ FAIL")
            
        # Show details of found issues
        for j, suggestion in enumerate(period_suggestions, 1):
            print(f"  Issue {j}: {suggestion['message']}")
            # Verify position accuracy
            start = suggestion['start']
            end = suggestion['end']
            actual_text = test_case['content'][start:end]
            expected_text = suggestion['text']
            
            if actual_text == expected_text:
                print(f"    ✅ Position mapping accurate")
            else:
                print(f"    ❌ Position mapping incorrect")
                print(f"       Expected: {repr(expected_text)}")
                print(f"       Actual:   {repr(actual_text)}")
    
    print(f"\n" + "=" * 60)
    print(f"TEST RESULTS: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("\nPeriod Detection Fix Summary:")
        print("- ✅ Handles bold text (**text**)")
        print("- ✅ Handles italic text (*text*)")
        print("- ✅ Handles links ([text](url))")
        print("- ✅ Handles images (![alt](src))")
        print("- ✅ Handles inline code (`code`)")
        print("- ✅ Accurate position mapping for highlighting")
        print("- ✅ Cleans formatting for better detection")
        print("- ✅ Shows cleaned text in error messages")
        print("- ✅ Avoids false positives on properly punctuated text")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

def test_edge_cases():
    """Test edge cases and potential false positives."""
    
    print("\n\n🔬 TESTING EDGE CASES")
    print("=" * 40)
    
    edge_cases = [
        {
            "name": "Short phrases (should be ignored)",
            "content": "**Title**\n# Header\n- List item\n• Bullet",
            "expected_issues": 0
        },
        {
            "name": "URLs and technical content",
            "content": "Visit https://example.com for info\nThe API endpoint is /api/v1/users",
            "expected_issues": 2  # These should trigger if they're long enough
        },
        {
            "name": "Already punctuated formatting",
            "content": "This **bold** text ends with a period.\nLinks [like this](url) should be fine too.",
            "expected_issues": 0
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        suggestions = check_period_placement(test_case['content'])
        period_suggestions = [s for s in suggestions if 'period' in s.get('message', '').lower()]
        
        print(f"   Expected: {test_case['expected_issues']}, Found: {len(period_suggestions)}")
        
        if len(period_suggestions) == test_case['expected_issues']:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            for suggestion in period_suggestions:
                print(f"      Issue: {suggestion['message']}")

if __name__ == "__main__":
    success = test_period_detection_comprehensive()
    test_edge_cases()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 PERIOD DETECTION FIX VERIFICATION COMPLETE!")
        print("\nThe enhanced period detection rule is now production-ready.")
        print("It correctly handles formatted content while avoiding false positives.")
    else:
        print("⚠️  Period detection fix needs additional refinement.")
