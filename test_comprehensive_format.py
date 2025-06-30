#!/usr/bin/env python3
"""
Comprehensive test to demonstrate the new structured AI suggestion format across multiple rules.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules import special_characters, can_may_terms, passive_voice, long_sentences

def test_comprehensive_structured_format():
    """Test the structured format across multiple rule types."""
    
    print("=== Comprehensive Test: Structured AI Suggestion Format ===\n")
    
    # Test cases designed to trigger various rules
    test_cases = [
        {
            "name": "Special Characters - Apostrophe",
            "text": "The API's are well documented and the URL's are correct.",
            "rule_module": special_characters,
            "expected_issues": ["apostrophe"]
        },
        {
            "name": "Special Characters - Ampersand", 
            "text": "Configure HTML & CSS files in the project.",
            "rule_module": special_characters,
            "expected_issues": ["ampersand"]
        },
        {
            "name": "Modal Verbs - Can Usage",
            "text": "You can download the file and you can save it locally.",
            "rule_module": can_may_terms,
            "expected_issues": ["modal verb"]
        },
        {
            "name": "Modal Verbs - May Usage",
            "text": "This feature may improve performance significantly.",
            "rule_module": can_may_terms,
            "expected_issues": ["may usage"]
        },
        {
            "name": "Passive Voice",
            "text": "The document was written by the team.",
            "rule_module": passive_voice,
            "expected_issues": ["passive voice"]
        },
        {
            "name": "Long Sentences",
            "text": "This is an extremely long sentence that contains way too many words and should definitely be broken down into smaller, more manageable pieces for better readability and comprehension.",
            "rule_module": long_sentences,
            "expected_issues": ["long sentence"]
        }
    ]
    
    all_formatted_correctly = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"TEST {i}: {test_case['name']}")
        print(f"Input text: '{test_case['text']}'")
        print("-" * 80)
        
        try:
            suggestions = test_case['rule_module'].check(test_case['text'])
            
            if suggestions:
                for j, suggestion in enumerate(suggestions, 1):
                    print(f"\nSuggestion {j}:")
                    print(suggestion)
                    
                    # Validate structure
                    has_issue = "Issue:" in suggestion
                    has_original = "Original sentence:" in suggestion  
                    has_ai_suggestion = "AI suggestion:" in suggestion
                    
                    structure_score = sum([has_issue, has_original, has_ai_suggestion])
                    
                    if structure_score == 3:
                        print("\n✅ FORMAT: Perfect structure (3/3 components)")
                    elif structure_score >= 2:
                        print(f"\n⚠️  FORMAT: Partial structure ({structure_score}/3 components)")
                        if not has_issue: print("   Missing: Issue")
                        if not has_original: print("   Missing: Original sentence")
                        if not has_ai_suggestion: print("   Missing: AI suggestion")
                        all_formatted_correctly = False
                    else:
                        print(f"\n❌ FORMAT: Poor structure ({structure_score}/3 components)")
                        all_formatted_correctly = False
            else:
                print("No suggestions generated")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_formatted_correctly = False
        
        print("\n" + "="*80 + "\n")
    
    # Summary
    print("SUMMARY:")
    if all_formatted_correctly:
        print("🎉 All suggestions are properly formatted with the new structure!")
        print("✅ Issue: [description]")
        print("✅ Original sentence: [sentence]") 
        print("✅ AI suggestion: [recommendation]")
    else:
        print("⚠️  Some suggestions still need formatting improvements.")
    
    return all_formatted_correctly

if __name__ == "__main__":
    test_comprehensive_structured_format()
