#!/usr/bin/env python3
"""
Test the improved period detection rule with formatted content.
Tests the fix for highlighting issues with bold text, links, and images.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.punctuation_rules import check_period_placement

def test_period_detection_with_formatting():
    """Test that period detection works correctly with various formatting."""
    
    print("🧪 Testing Period Detection with Formatted Content")
    print("=" * 60)
    
    # Test cases with various formatting issues
    test_cases = [
        {
            "name": "Bold text missing period",
            "text": "This sentence has **bold text** but no period\nThis sentence has proper punctuation.",
            "expected_issues": 1,
            "should_highlight": "This sentence has **bold text** but no period"
        },
        {
            "name": "Link missing period", 
            "text": "Check out this [great website](https://example.com) for more info\nThis sentence is fine.",
            "expected_issues": 1,
            "should_highlight": "Check out this [great website](https://example.com) for more info"
        },
        {
            "name": "Image with missing period",
            "text": "Here is an image ![alt text](image.jpg) showing the result\nProper sentence with period.",
            "expected_issues": 1,
            "should_highlight": "Here is an image ![alt text](image.jpg) showing the result"
        },
        {
            "name": "Multiple formatting elements",
            "text": "This **bold** sentence with a [link](url) and ![image](src) needs period\nThis one is correct.",
            "expected_issues": 1,
            "should_highlight": "This **bold** sentence with a [link](url) and ![image](src) needs period"
        },
        {
            "name": "Inline code missing period",
            "text": "Use the `print()` function to display output\nThis sentence ends properly.",
            "expected_issues": 1,
            "should_highlight": "Use the `print()` function to display output"
        },
        {
            "name": "No issues - proper formatting",
            "text": "This **bold** sentence with a [link](url) ends properly.\nThis `code` example is also correct.",
            "expected_issues": 0,
            "should_highlight": None
        },
        {
            "name": "Short phrases should be ignored",
            "text": "**Title**\n# Header\n- List item\nThis is a proper sentence that needs a period",
            "expected_issues": 1,
            "should_highlight": "This is a proper sentence that needs a period"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Text: {repr(test_case['text'])}")
        
        suggestions = check_period_placement(test_case['text'])
        
        print(f"   Found {len(suggestions)} issues (expected: {test_case['expected_issues']})")
        
        # Check if we found the expected number of issues
        if len(suggestions) == test_case['expected_issues']:
            print("   ✅ Correct number of issues detected")
        else:
            print("   ❌ Wrong number of issues detected")
            
        # Check if we're highlighting the right text
        if test_case['should_highlight']:
            if suggestions and test_case['should_highlight'] in suggestions[0]['text']:
                print("   ✅ Correctly highlighting target text")
            else:
                print("   ❌ Not highlighting expected text")
                if suggestions:
                    print(f"      Actually highlighting: {repr(suggestions[0]['text'])}")
        
        # Show details of found issues
        for j, suggestion in enumerate(suggestions):
            print(f"   Issue {j+1}: {suggestion['message']}")
            print(f"   Position: {suggestion['start']}-{suggestion['end']}")
            print(f"   Text: {repr(suggestion['text'])}")

def test_position_accuracy():
    """Test that position mapping is accurate for highlighting."""
    
    print("\n\n🎯 Testing Position Accuracy")
    print("=" * 40)
    
    text = """First line with proper punctuation.
This **bold** line needs a period
Third line is [a link](url) missing period
Final line with ![image](src) no period"""
    
    suggestions = check_period_placement(text)
    
    print(f"Text:\n{repr(text)}")
    print(f"\nFound {len(suggestions)} suggestions:")
    
    for i, suggestion in enumerate(suggestions, 1):
        start = suggestion['start']
        end = suggestion['end']
        highlighted_text = text[start:end]
        
        print(f"\nSuggestion {i}:")
        print(f"  Message: {suggestion['message']}")
        print(f"  Position: {start}-{end}")
        print(f"  Expected text: {repr(suggestion['text'])}")
        print(f"  Actual text at position: {repr(highlighted_text)}")
        
        if highlighted_text == suggestion['text']:
            print("  ✅ Position mapping is accurate")
        else:
            print("  ❌ Position mapping is incorrect")

if __name__ == "__main__":
    test_period_detection_with_formatting()
    test_position_accuracy()
    
    print("\n" + "=" * 60)
    print("🎉 Period Detection Fix Testing Complete!")
    print("\nThe enhanced period detection rule should now:")
    print("- ✅ Handle bold text (**text**)")
    print("- ✅ Handle links ([text](url))")  
    print("- ✅ Handle images (![alt](src))")
    print("- ✅ Handle inline code (`code`)")
    print("- ✅ Provide accurate position mapping for highlighting")
    print("- ✅ Show cleaned text in error messages")
