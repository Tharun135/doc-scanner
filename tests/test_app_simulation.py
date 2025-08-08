#!/usr/bin/env python3

"""
Test the complete AI suggestion pipeline as the app would use it.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import ai_engine

def test_app_simulation():
    """Simulate how the app calls the AI suggestion system."""
    
    print("🧪 TESTING APP SIMULATION")
    print("=" * 60)
    
    # Simulate various real scenarios
    test_scenarios = [
        {
            "issue": "Passive Voice",
            "feedback": "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'.",
            "sentence": "The selected configuration files are updated.",
            "expected_keywords": ["system updates", "active voice"]
        },
        {
            "issue": "Above Reference", 
            "feedback": "Avoid using 'above' to refer to previous content; use specific references.",
            "sentence": "Use the configuration mentioned above for best results.",
            "expected_keywords": ["OPTION 1", "previous section", "discussed"]
        },
        {
            "issue": "Long Sentence",
            "feedback": "This sentence is too long and should be broken into shorter, clearer sentences.",
            "sentence": "You can configure the system settings through the admin panel which provides access to various configuration options and allows you to customize the behavior.",
            "expected_keywords": ["OPTION 1 has sentence 1", "sentence 2"]
        },
        {
            "issue": "Modal Verb",
            "feedback": "Avoid unnecessary modal verbs like 'may' when giving direct instructions.",
            "sentence": "You may now proceed to configure the settings.",
            "expected_keywords": ["OPTION", "proceed to configure", "WHY"]
        }
    ]
    
    success_count = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 SCENARIO {i}: {scenario['issue']}")
        print(f"   Original: {scenario['sentence']}")
        
        # Call the AI suggestion system like the app does
        result = ai_engine.generate_contextual_suggestion(
            feedback_text=scenario['feedback'],
            sentence_context=scenario['sentence'],
            document_type="technical"
        )
        
        suggestion = result.get('suggestion', '')
        method = result.get('method', 'unknown')
        
        print(f"   Method: {method}")
        print(f"   Result: {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
        
        # Check if suggestion is good
        is_good = False
        
        # Check if it contains expected improvement keywords
        if any(keyword.lower() in suggestion.lower() for keyword in scenario['expected_keywords']):
            is_good = True
        
        # Check if it's not just echoing the original
        if scenario['sentence'] in suggestion and "OPTION" not in suggestion:
            is_good = False
            
        # Check if it's the old template response
        if suggestion.startswith(f"Convert To Active Voice: {scenario['sentence']}"):
            is_good = False
            
        if is_good:
            print("   ✅ GOOD: Provides meaningful improvements")
            success_count += 1
        else:
            print("   ❌ BAD: Not providing proper improvements")
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: {success_count}/{len(test_scenarios)} scenarios working correctly")
    
    if success_count == len(test_scenarios):
        print("🎉 ALL SCENARIOS PASS: AI suggestion system is working!")
        return True
    else:
        print("❌ SOME SCENARIOS FAIL: More fixes needed!")
        return False

if __name__ == "__main__":
    test_app_simulation()
