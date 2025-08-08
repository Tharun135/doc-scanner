#!/usr/bin/env python3

"""
Test the modified JSON/XML capitalization rule.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.technical_terms import check

def test_json_xml_capitalization():
    """Test that JSON/XML capitalization rule works correctly."""
    
    test_cases = [
        {
            "text": "The json format is widely used.",
            "should_flag": True,
            "description": "General json format reference - should be flagged"
        },
        {
            "text": "Save the data as a .json file.",
            "should_flag": False,
            "description": "File extension .json - should NOT be flagged"
        },
        {
            "text": "The .json extension is common.",
            "should_flag": False,
            "description": "File extension .json - should NOT be flagged"
        },
        {
            "text": "Use xml for configuration.",
            "should_flag": True,
            "description": "General xml format reference - should be flagged"
        },
        {
            "text": "Open the .xml file.",
            "should_flag": False,
            "description": "File extension .xml - should NOT be flagged"
        },
        {
            "text": "Export as .xml format.",
            "should_flag": False,
            "description": "File extension .xml - should NOT be flagged"
        },
        {
            "text": "JSON is already correct.",
            "should_flag": False,
            "description": "Already capitalized JSON - should NOT be flagged"
        },
        {
            "text": "The config.json file contains json data.",
            "should_flag": True,
            "description": "Mixed: .json extension (OK) and json data (should be flagged)"
        }
    ]
    
    print("🧪 TESTING JSON/XML CAPITALIZATION RULE")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TEST {i}: {test_case['description']}")
        print(f"   Text: \"{test_case['text']}\"")
        
        # Run the rule check
        suggestions = check(test_case['text'])
        
        # Check for JSON/XML capitalization suggestions
        json_xml_suggestions = [s for s in suggestions if 
                               ('json' in s.lower() and 'JSON' in s) or 
                               ('xml' in s.lower() and 'XML' in s)]
        
        has_suggestion = len(json_xml_suggestions) > 0
        
        print(f"   Found suggestions: {json_xml_suggestions}")
        
        if test_case['should_flag'] and has_suggestion:
            print("   ✅ CORRECT: Rule flagged as expected")
        elif not test_case['should_flag'] and not has_suggestion:
            print("   ✅ CORRECT: Rule did not flag as expected")
        elif test_case['should_flag'] and not has_suggestion:
            print("   ❌ ERROR: Should have flagged but didn't")
            all_passed = False
        else:
            print("   ❌ ERROR: Should not have flagged but did")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL TESTS PASSED: JSON/XML rule working correctly!")
    else:
        print("❌ SOME TESTS FAILED: Rule needs more adjustment!")
    
    return all_passed

if __name__ == "__main__":
    test_json_xml_capitalization()
