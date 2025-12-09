#!/usr/bin/env python3
"""
Comprehensive test including the user's documentation examples
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.grammar_rules import check

def comprehensive_test_with_docs():
    """Test including documentation patterns and the user's examples"""
    
    test_cases = {
        "🔧 Technical Documentation (Should NOT trigger)": [
            ("vals: data points published in the payload.", False),
            ("id: unique identification of data point.", False), 
            ("qc: quality code with specific integer value.", False),
            ("val: value of the Tag based on data type.", False),
            ("api: application programming interface.", False),
            ("url: uniform resource locator.", False),
            ("json: JavaScript object notation format.", False),
        ],
        
        "🔧 Original Technical Codes (Should NOT trigger)": [
            ("ie/d/j/simatic/v1/slmp1/dp/r//default", False),
            ("api/v1/users", False),
            ("src/components/header.js", False),
        ],
        
        "📄 File References (Should NOT trigger)": [
            ("config.json", False),
            ("package.json", False),
            ("readme.md", False),
        ],
        
        "🌐 URLs (Should NOT trigger)": [
            ("https://example.com/path", False),
            ("http://api.service.com", False),
            ("ftp://files.example.org", False),
        ],
        
        "💬 Code References (Should NOT trigger)": [
            ("object.method()", False),
            ("variable.property", False),
        ],
        
        "📝 Markdown Syntax (Should NOT trigger)": [
            ('info "This is a notice"', False),
            ('warning "This is a warning"', False),
        ],
        
        "❌ Legitimate Grammar Issues (SHOULD trigger)": [
            ("this sentence should start with capital", True),
            ("another example of incorrect capitalization", True),
            ("it is in ISO 8601 Zulu format.", True),  # This should be "It is..."
            ("here is one more test case", True),
        ],
        
        "✅ Correct Sentences (Should NOT trigger)": [
            ("This sentence starts correctly.", False),
            ("Another properly capitalized sentence.", False),
            ("It is in ISO 8601 Zulu format.", False),  # Correctly capitalized
        ],
    }
    
    print("COMPREHENSIVE TEST WITH DOCUMENTATION PATTERNS")
    print("=" * 60)
    
    all_passed = True
    total_tests = 0
    passed_tests = 0
    
    for category, test_list in test_cases.items():
        print(f"\n{category}")
        print("-" * 50)
        
        for test_text, should_trigger in test_list:
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
                all_passed = False
            
            # Truncate long text for display
            display_text = test_text if len(test_text) <= 45 else test_text[:42] + "..."
            
            print(f"  {status} {display_text}")
            
            if not passed:
                expected = "Should trigger" if should_trigger else "Should NOT trigger"
                actual = "Triggered" if triggered else "Did not trigger"
                print(f"      Expected: {expected} | Actual: {actual}")
    
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
        print("✅ Documentation patterns excluded (id:, vals:, etc.)")
        print("✅ Technical codes excluded") 
        print("✅ Legitimate grammar issues still caught")
        print("✅ Normal functionality preserved")
    else:
        print("\n❌ Some tests failed")
    
    return all_passed

if __name__ == "__main__":
    comprehensive_test_with_docs()
