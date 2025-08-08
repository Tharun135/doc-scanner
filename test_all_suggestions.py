#!/usr/bin/env python3

"""
Comprehensive test script to check all types of AI suggestions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_suggestion_types():
    """Test various types of AI suggestions to find which ones are broken."""
    
    from app.ai_improvement import ai_engine
    
    test_cases = [
        {
            "name": "Passive Voice",
            "feedback": "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'.",
            "sentence": "The selected configuration files are updated.",
            "expected_change": True
        },
        {
            "name": "Above Reference", 
            "feedback": "Avoid using 'above' to refer to previous content; use specific references.",
            "sentence": "Common Configurator creates a JSON configuration file that is identical to the second configuration mentioned above.",
            "expected_change": True
        },
        {
            "name": "Long Sentence",
            "feedback": "This sentence is too long and should be broken into shorter, clearer sentences.",
            "sentence": "You can configure the application settings through the main configuration panel which allows you to set various parameters and options.",
            "expected_change": True
        },
        {
            "name": "First Person",
            "feedback": "Avoid using first person pronouns in technical documentation.",
            "sentence": "We recommend that you configure the settings carefully.",
            "expected_change": True
        },
        {
            "name": "Modal Verb",
            "feedback": "Avoid unnecessary modal verbs like 'may' when giving direct instructions.",
            "sentence": "You may now click the Save button to save your changes.",
            "expected_change": True
        },
        {
            "name": "General Writing",
            "feedback": "Improve clarity and conciseness of this sentence.",
            "sentence": "Due to the fact that the configuration is very very important, you should be careful.",
            "expected_change": True
        }
    ]
    
    print("🧪 COMPREHENSIVE AI SUGGESTION TEST")
    print("=" * 80)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TEST CASE {i}: {test_case['name']}")
        print("-" * 60)
        print(f"Feedback: {test_case['feedback']}")
        print(f"Original: {test_case['sentence']}")
        print()
        
        try:
            result = ai_engine.generate_contextual_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence'],
                document_type="technical"
            )
            
            suggestion = result.get('suggestion', '')
            method = result.get('method', 'unknown')
            
            print(f"🤖 AI Result ({method}):")
            print(f"   {suggestion}")
            
            # Check if suggestion is just echoing the original
            original_in_suggestion = test_case['sentence'] in suggestion
            has_improvements = not original_in_suggestion or "OPTION" in suggestion
            
            if has_improvements:
                print("   ✅ GOOD: Provides actual improvements")
            else:
                print("   ❌ BAD: Just echoing original sentence")
                all_passed = False
                
            # Look for specific improvement indicators
            if "OPTION 1:" in suggestion and "OPTION 2:" in suggestion:
                print("   ✅ GOOD: Multiple options provided")
            elif suggestion.strip() == f"Convert To Active Voice: {test_case['sentence']}":
                print("   ❌ BAD: Template response without actual conversion")
                all_passed = False
            elif "Consider revising:" in suggestion and test_case['sentence'] in suggestion:
                print("   ❌ BAD: Generic 'Consider revising' response")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED: AI suggestions are working correctly!")
    else:
        print("❌ SOME TESTS FAILED: AI suggestions need more fixes!")
    
    return all_passed

if __name__ == "__main__":
    test_all_suggestion_types()
