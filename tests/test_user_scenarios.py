#!/usr/bin/env python3

"""
Test the user's specific scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.technical_terms import check

def test_user_scenarios():
    """Test the user's specific concern about file extensions."""
    
    user_scenarios = [
        {
            "text": "Save the configuration as .json file.",
            "description": "User's concern: .json file extension should NOT be flagged",
            "should_flag": False
        },
        {
            "text": "The .xml format is widely supported.",
            "description": "User's concern: .xml file extension should NOT be flagged",
            "should_flag": False
        },
        {
            "text": "Use json for data exchange.",
            "description": "General json format - SHOULD be flagged",
            "should_flag": True
        },
        {
            "text": "Parse xml documents efficiently.",
            "description": "General xml format - SHOULD be flagged", 
            "should_flag": True
        },
        {
            "text": "Export data to .json and process xml content.",
            "description": "Mixed: .json (OK) and xml format (flag)",
            "should_flag": True
        },
        {
            "text": "The config.json contains json data for xml processing.",
            "description": "Complex: .json (OK), json format (flag), xml format (flag)",
            "should_flag": True
        }
    ]
    
    print("🧪 TESTING USER'S SPECIFIC SCENARIOS")
    print("=" * 70)
    print("User's request: File extensions like .json/.xml should NOT be flagged")
    print("Only general format references (json/xml) should be flagged")
    print("=" * 70)
    
    all_passed = True
    
    for i, scenario in enumerate(user_scenarios, 1):
        print(f"\n📝 SCENARIO {i}: {scenario['description']}")
        print(f"   Text: \"{scenario['text']}\"")
        
        # Run the rule check
        suggestions = check(scenario['text'])
        
        # Check for JSON/XML capitalization suggestions
        json_xml_suggestions = [s for s in suggestions if 
                               ('json' in s.lower() and 'JSON' in s) or 
                               ('xml' in s.lower() and 'XML' in s)]
        
        has_flags = len(json_xml_suggestions) > 0
        
        print(f"   Suggestions: {json_xml_suggestions}")
        print(f"   Should flag: {scenario['should_flag']}")
        print(f"   Actually flagged: {has_flags}")
        
        if scenario['should_flag'] == has_flags:
            print("   ✅ CORRECT: Behavior matches expectation")
        else:
            print("   ❌ ERROR: Unexpected behavior")
            all_passed = False
    
    print(f"\n{'='*70}")
    if all_passed:
        print("🎉 USER'S REQUEST FULLY SATISFIED!")
        print("✅ File extensions (.json/.xml) are NOT flagged")
        print("✅ General format references (json/xml) ARE flagged")
    else:
        print("❌ USER'S REQUEST NOT FULLY SATISFIED!")
    
    return all_passed

if __name__ == "__main__":
    test_user_scenarios()
