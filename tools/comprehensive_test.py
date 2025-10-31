#!/usr/bin/env python3
"""
Comprehensive test to verify the complete fix for the capital letter rule issue
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.grammar_rules import check

def comprehensive_test():
    """Comprehensive test covering all scenarios"""
    
    print("COMPREHENSIVE CAPITAL LETTER RULE TEST")
    print("=" * 60)
    print("Testing fix for issue: 'ie/d/j/simatic/v1/slmp1/dp/r//default'")
    print()
    
    # Test categories
    test_categories = {
        "🔧 Technical Codes (Should NOT trigger)": [
            ("ie/d/j/simatic/v1/slmp1/dp/r//default", False),  # Original issue
            ("api/v1/users", False),
            ("src/components/header.js", False),
            ("config/settings/production.json", False),
            ("lib/utils/string-helpers.ts", False),
            ("docs/api/reference", False),
        ],
        
        "📄 File References (Should NOT trigger)": [
            ("config.json", False),
            ("package.json", False),
            ("readme.md", False),
            ("index.html", False),
        ],
        
        "🌐 URLs (Should NOT trigger)": [
            ("https://example.com/path", False),
            ("http://api.service.com", False),
            ("ftp://files.example.org", False),
        ],
        
        "💬 Code References (Should NOT trigger)": [
            ("object.method()", False),
            ("variable.property", False),
            ("class.function.call", False),
        ],
        
        "📝 Markdown Syntax (Should NOT trigger)": [
            ('info "This is a notice"', False),
            ('warning "This is a warning"', False),
            ('note "Important information"', False),
        ],
        
        "✅ Normal Text - Correct (Should NOT trigger)": [
            ("This sentence starts correctly.", False),
            ("Another properly capitalized sentence.", False),
            ("Here is a third correct example.", False),
        ],
        
        "❌ Normal Text - Incorrect (SHOULD trigger)": [
            ("this sentence should start with capital", True),
            ("another example of incorrect capitalization", True),
            ("here is one more test case", True),
            ("the API endpoint requires proper capitalization", True),
        ],
    }
    
    all_passed = True
    total_tests = 0
    passed_tests = 0
    
    for category, test_cases in test_categories.items():
        print(f"\n{category}")
        print("-" * 50)
        
        category_passed = True
        
        for test_text, should_trigger in test_cases:
            total_tests += 1
            suggestions = check(test_text)
            capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
            
            triggered = len(capital_suggestions) > 0
            passed = triggered == should_trigger
            
            if passed:
                passed_tests += 1
                status = "✅"
            else:
                status = "❌"
                category_passed = False
                all_passed = False
            
            # Truncate long text for display
            display_text = test_text if len(test_text) <= 40 else test_text[:37] + "..."
            
            print(f"  {status} {display_text}")
            
            if not passed:
                expected = "Should trigger" if should_trigger else "Should NOT trigger"
                actual = "Triggered" if triggered else "Did not trigger"
                print(f"      Expected: {expected} | Actual: {actual}")
        
        if not category_passed:
            print(f"    ❌ Some tests in this category failed!")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests / total_tests * 100):.1f}%")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Issue fixed: Technical codes are now properly excluded")
        print("✅ Normal functionality preserved: Regular sentences still checked")
        print("✅ No false positives: File paths, URLs, and code references ignored")
    else:
        print("\n❌ Some tests failed - the fix needs more work")
    
    return all_passed

if __name__ == "__main__":
    comprehensive_test()
