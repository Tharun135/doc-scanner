#!/usr/bin/env python3
"""
Test the improved modal verb handling.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import EnhancedAISuggestionEngine

def test_modal_verb_improvements():
    """Test the improved modal verb suggestions."""
    print("🧪 TESTING IMPROVED MODAL VERB HANDLING")
    print("=" * 60)
    
    engine = EnhancedAISuggestionEngine()
    
    test_cases = [
        {
            "name": "Problematic migration case",
            "feedback": "Use of modal verb 'can' - should describe direct action", 
            "sentence": "You can migrate an existing configuration from SIMATIC S7 Connector in two ways:"
        },
        {
            "name": "User access case",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "Users can access their data through the dashboard."
        },
        {
            "name": "System processing case", 
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "The system can process multiple requests simultaneously."
        },
        {
            "name": "Simple you can case",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "You can configure the settings from the main menu."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Original: {test_case['sentence']}")
        print(f"Feedback: {test_case['feedback']}")
        
        try:
            result = engine.generate_smart_fallback_suggestion(
                test_case['feedback'], 
                test_case['sentence']
            )
            
            print(f"✅ Result:")
            print(f"   Suggestion: {result['suggestion']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Method: {result['method']}")
            
            # Check if it contains corrected text
            if "CORRECTED TEXT:" in result['suggestion']:
                # Extract the corrected text
                lines = result['suggestion'].split('\n')
                corrected_line = [line for line in lines if line.startswith("CORRECTED TEXT:")][0]
                corrected_text = corrected_line.replace("CORRECTED TEXT:", "").strip().strip('"')
                print(f"   ✨ Corrected Text: {corrected_text}")
                
                # Check if it's an improvement
                if "migrate" in test_case['sentence'].lower() and "You migrate" in corrected_text:
                    print(f"   ❌ Still has grammar issue: 'You migrate' is not grammatically correct")
                elif corrected_text and corrected_text != test_case['sentence']:
                    print(f"   ✅ Improved suggestion!")
                else:
                    print(f"   ⚠️  No change made")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_modal_verb_improvements()
