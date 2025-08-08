#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.simple_present_tense import check

def test_problematic_sentence():
    """Test the sentence that was incorrectly flagged"""
    test_sentence = "Open the Edge Devices window In IEM and select the IED where the EtherNet/IP IO Connector is running."
    
    print("="*80)
    print("TESTING SIMPLE PRESENT TENSE RULE FIX")
    print("="*80)
    print(f"Test sentence: {test_sentence}")
    print()
    
    try:
        result = check(test_sentence)
        print(f"Number of violations found: {len(result)}")
        
        if result:
            print("\n❌ VIOLATIONS FOUND:")
            for i, violation in enumerate(result, 1):
                print(f"  {i}. {violation}")
            print("\n🔴 FAILED: This sentence should NOT be flagged as it's grammatically correct.")
        else:
            print("\n✅ SUCCESS: No violations found!")
            print("🟢 PASSED: The sentence is correctly recognized as valid.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)

def test_other_sentences():
    """Test other sentences to ensure the fix doesn't break valid cases"""
    test_cases = [
        # Should still be flagged (inappropriate continuous tense)
        ("The user is clicking the button repeatedly.", True),
        ("The system is processing the data every hour.", True),
        
        # Should NOT be flagged (appropriate continuous tense)
        ("Check that the service is running before proceeding.", False),
        ("Verify the server is operating correctly.", False),
        ("Find the component where the process is executing.", False),
        ("Select the device that is monitoring the network.", False),
    ]
    
    print("\nTESTING OTHER CASES:")
    print("-" * 40)
    
    for sentence, should_be_flagged in test_cases:
        result = check(sentence)
        has_violations = len(result) > 0
        
        status = "✅" if (has_violations == should_be_flagged) else "❌"
        expected = "SHOULD be flagged" if should_be_flagged else "should NOT be flagged"
        actual = "WAS flagged" if has_violations else "was NOT flagged"
        
        print(f"{status} {sentence}")
        print(f"    Expected: {expected}, Actual: {actual}")
        if has_violations:
            for violation in result:
                print(f"    Violation: {violation}")
        print()

if __name__ == "__main__":
    test_problematic_sentence()
    test_other_sentences()
