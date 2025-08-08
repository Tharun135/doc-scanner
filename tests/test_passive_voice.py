#!/usr/bin/env python3

"""
Test just the passive voice fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import ai_engine

def test_passive_voice():
    """Test passive voice conversion specifically."""
    
    test_cases = [
        "The selected configuration files are updated.",
        "The report is updated by the system.",
        "Configuration files are displayed on the screen.",
        "The data is processed automatically."
    ]
    
    feedback = "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'."
    
    print("🧪 TESTING PASSIVE VOICE CONVERSIONS")
    print("=" * 60)
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n📝 TEST {i}: {sentence}")
        
        result = ai_engine.generate_contextual_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="technical"
        )
        
        suggestion = result.get('suggestion', '')
        print(f"🤖 Result: {suggestion}")
        
        if sentence in suggestion:
            print("   ❌ Still contains original")
        else:
            print("   ✅ Successfully converted")

if __name__ == "__main__":
    test_passive_voice()
