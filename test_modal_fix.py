#!/usr/bin/env python3

# Test script to verify the modal verb duplication fix
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from rules.simple_present_tense import check

def test_modal_duplicates():
    """Test that modal verb suggestions are not duplicated"""
    
    # Test case 1: Single modal verb
    test_text1 = "You can configure an IEC 61850 data source in the Common Configurator."
    suggestions1 = check(test_text1)
    print(f"Test 1 - Single modal:")
    print(f"Text: {test_text1}")
    print(f"Suggestions count: {len(suggestions1)}")
    for i, suggestion in enumerate(suggestions1):
        print(f"  {i+1}. {suggestion}")
    print()
    
    # Test case 2: Multiple modal verbs in same sentence
    test_text2 = "You can configure the system and you can also modify the settings."
    suggestions2 = check(test_text2)
    print(f"Test 2 - Multiple modals in same sentence:")
    print(f"Text: {test_text2}")
    print(f"Suggestions count: {len(suggestions2)}")
    for i, suggestion in enumerate(suggestions2):
        print(f"  {i+1}. {suggestion}")
    print()
    
    # Test case 3: Multiple sentences with modal verbs
    test_text3 = "You can configure the data source. You should also check the settings."
    suggestions3 = check(test_text3)
    print(f"Test 3 - Multiple sentences with modals:")
    print(f"Text: {test_text3}")
    print(f"Suggestions count: {len(suggestions3)}")
    for i, suggestion in enumerate(suggestions3):
        print(f"  {i+1}. {suggestion}")
    print()
    
    # Test case 4: Same sentence repeated in text
    test_text4 = "You can configure the system. You can configure the system."
    suggestions4 = check(test_text4)
    print(f"Test 4 - Same sentence repeated:")
    print(f"Text: {test_text4}")
    print(f"Suggestions count: {len(suggestions4)}")
    for i, suggestion in enumerate(suggestions4):
        print(f"  {i+1}. {suggestion}")
    print()
    
    # Validation
    print("VALIDATION:")
    print(f"Test 1 should have 1 suggestion: {'✓' if len(suggestions1) == 1 else '✗'}")
    print(f"Test 2 should have 1 suggestion: {'✓' if len(suggestions2) == 1 else '✗'}")
    print(f"Test 3 should have 2 suggestions: {'✓' if len(suggestions3) == 2 else '✗'}")
    print(f"Test 4 should have 2 suggestions: {'✓' if len(suggestions4) == 2 else '✗'}")

if __name__ == "__main__":
    test_modal_duplicates()
