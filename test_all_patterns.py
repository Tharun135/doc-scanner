#!/usr/bin/env python3
"""Comprehensive test for all AI suggestion patterns."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_all_patterns():
    """Test all problematic patterns to ensure they're fixed."""
    
    test_cases = [
        {
            "name": "Must be met pattern",
            "feedback": "Convert to active voice",
            "sentence": "The following requirement must be met:",
            "expect_good": True
        },
        {
            "name": "Are displayed pattern",
            "feedback": "passive voice detected", 
            "sentence": "The results are displayed on screen.",
            "expect_good": True
        },
        {
            "name": "Is processed pattern",
            "feedback": "Convert to active voice",
            "sentence": "The data is processed by the system.",
            "expect_good": True
        },
        {
            "name": "Are generated pattern",
            "feedback": "passive voice detected",
            "sentence": "The logs are generated automatically.",
            "expect_good": True
        },
        {
            "name": "Long sentence pattern",
            "feedback": "sentence too long",
            "sentence": "The new feature allows users to configure their settings, customize their preferences, and manage their data all in one centralized location.",
            "expect_good": True
        }
    ]
    
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        print("=== Comprehensive AI Suggestion Test ===\n")
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"--- Test {i}: {test_case['name']} ---")
            print(f"Sentence: {test_case['sentence']}")
            
            result = get_enhanced_ai_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence']
            )
            
            suggestion = result.get('suggestion', '')
            method = result.get('method', 'unknown')
            
            print(f"Method: {method}")
            
            # Check for common broken patterns
            issues = []
            if "you can access:" in suggestion.lower():
                issues.append("Contains 'you can access:' pattern")
            if "system handles following" in suggestion.lower():
                issues.append("Contains broken 'system handles' pattern") 
            if "users can update following" in suggestion.lower():
                issues.append("Contains broken 'users can update' pattern")
            if suggestion.count("OPTION 1:") > 0:
                option1_line = [line for line in suggestion.split('\n') if 'OPTION 1:' in line][0]
                if test_case['sentence'] in option1_line and "must be met" not in test_case['sentence']:
                    issues.append("Option 1 is identical to original (non-'must be met' case)")
            
            if issues:
                print(f"❌ ISSUES FOUND: {', '.join(issues)}")
                all_passed = False
            else:
                print(f"✅ LOOKS GOOD")
            
            print(f"Suggestion preview: {suggestion[:100]}...")
            print()
        
        if all_passed:
            print("🎉 ALL TESTS PASSED! No broken patterns detected.")
        else:
            print("⚠️  Some issues still exist. Review the output above.")
            
        return all_passed
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_all_patterns()
