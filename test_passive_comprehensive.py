#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import LlamaIndexAISuggestionEngine

def test_passive_voice_comprehensive():
    print("="*80)
    print("COMPREHENSIVE PASSIVE VOICE AI SUGGESTIONS TEST")
    print("="*80)
    
    ai_manager = LlamaIndexAISuggestionEngine()
    
    test_cases = [
        {
            "sentence": "These values are derived during the XSLT Transformation step in Model Maker.",
            "feedback": "Convert to active voice",
            "description": "Original reported issue"
        },
        {
            "sentence": "Data is processed by the system every hour.",
            "feedback": "Convert to active voice",
            "description": "Generic passive with agent"
        },
        {
            "sentence": "The configuration options are displayed in the interface.",
            "feedback": "Convert to active voice", 
            "description": "Simple passive without agent"
        },
        {
            "sentence": "Logs are generated when the application starts.",
            "feedback": "Convert to active voice",
            "description": "Passive with condition"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print("-" * 50)
        print(f"Original: {test_case['sentence']}")
        
        try:
            result = ai_manager.generate_contextual_suggestion(test_case['feedback'], test_case['sentence'])
            suggestion_text = result.get('suggestion', '')
            
            # Extract options
            lines = suggestion_text.split('\n')
            options = [line for line in lines if line.startswith('OPTION')]
            
            print("Suggestions:")
            for option in options:
                print(f"  {option}")
                
                # Quick analysis
                if "are " in option.lower() or "is " in option.lower():
                    if "get " in option.lower() and "are " not in option.replace("get ", ""):
                        print("    ⚠️  Weak: Uses 'get' conversion")
                    else:
                        print("    ❌ Still passive")
                elif "you " in option.lower():
                    print("    ✅ Good: User-focused active voice")
                elif any(word in option.lower() for word in ["system", "model maker", "interface"]):
                    print("    ✅ Good: System-focused active voice")
                else:
                    print("    ✅ Good: Active voice")
                    
            # Check for "User" vs "You"
            if "user" in suggestion_text.lower() and "you" not in suggestion_text.lower():
                print("  ❌ Uses 'User' instead of 'You'")
            elif "you" in suggestion_text.lower():
                print("  ✅ Uses 'You' appropriately")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_passive_voice_comprehensive()
