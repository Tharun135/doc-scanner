#!/usr/bin/env python3

"""
Additional edge case tests for JSON/XML capitalization rule.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.technical_terms import check

def test_additional_edge_cases():
    """Test additional edge cases for the JSON/XML rule."""
    
    edge_cases = [
        {
            "text": "The data.json and config.xml files use json and xml formats.",
            "expected_flags": 2,
            "description": "Multiple file extensions + format references"
        },
        {
            "text": "Parse the .json file using a json parser.",
            "expected_flags": 1,
            "description": "File extension + format reference"
        },
        {
            "text": "Export to .xml or use xml serialization.",
            "expected_flags": 1,
            "description": "File extension + serialization reference"
        },
        {
            "text": "JSON and XML are standard formats.",
            "expected_flags": 0,
            "description": "Already correctly capitalized"
        },
        {
            "text": "Create a .json.backup file.",
            "expected_flags": 0,
            "description": "Complex file extension"
        },
        {
            "text": "The xml format is better than json format.",
            "expected_flags": 2,
            "description": "Both formats mentioned"
        }
    ]
    
    print("🧪 TESTING ADDITIONAL EDGE CASES")
    print("=" * 60)
    
    all_passed = True
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n📝 TEST {i}: {test_case['description']}")
        print(f"   Text: \"{test_case['text']}\"")
        
        # Run the rule check
        suggestions = check(test_case['text'])
        
        # Count JSON/XML capitalization suggestions
        json_xml_count = len([s for s in suggestions if 
                             ('json' in s.lower() and 'JSON' in s) or 
                             ('xml' in s.lower() and 'XML' in s)])
        
        print(f"   Expected flags: {test_case['expected_flags']}")
        print(f"   Actual flags: {json_xml_count}")
        print(f"   Suggestions: {[s for s in suggestions if 'json' in s.lower() or 'xml' in s.lower()]}")
        
        if json_xml_count == test_case['expected_flags']:
            print("   ✅ CORRECT: Flag count matches expectation")
        else:
            print("   ❌ ERROR: Flag count doesn't match")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL EDGE CASES PASS: Rule is robust!")
    else:
        print("❌ SOME EDGE CASES FAIL: Rule needs refinement!")
    
    return all_passed

if __name__ == "__main__":
    test_additional_edge_cases()
