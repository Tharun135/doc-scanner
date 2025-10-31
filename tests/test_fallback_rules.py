#!/usr/bin/env python3
"""
Test the rule-based fallback system for passive voice conversion.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from intelligent_ai_improvement import IntelligentAISuggestionEngine
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_fallback_rules():
    """Test the rule-based fallback suggestions directly."""
    
    print("🧪 TESTING RULE-BASED FALLBACK SYSTEM")
    print("=" * 50)
    
    # Initialize the system
    ai_engine = IntelligentAISuggestionEngine()
    
    # Test sentences with passive voice patterns
    test_cases = [
        "The available connectors are shown.",
        "Data is displayed in the dashboard.",
        "Reports are generated automatically.",
        "Configuration settings are provided.",
        "Information is shown in the sidebar."
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n🔍 TEST {i}: {sentence}")
        print("-" * 40)
        
        try:
            # Test the fallback function directly
            suggestion, explanation = ai_engine._generate_fallback_suggestion(sentence, "test_passive")
            
            original_words = len(sentence.split())
            suggestion_words = len(suggestion.split())
            
            print(f"✅ ORIGINAL ({original_words} words): {sentence}")
            print(f"🔧 SUGGESTION ({suggestion_words} words): {suggestion}")
            print(f"📝 EXPLANATION: {explanation}")
            
            # Check if it's actually improved
            if suggestion != sentence:
                print(f"✅ IMPROVED: Changed from original")
                
                # Check for passive voice patterns
                passive_patterns = ['are shown', 'is displayed', 'are generated', 'are provided', 'is shown']
                found_passive = any(pattern in sentence.lower() for pattern in passive_patterns)
                still_passive = any(pattern in suggestion.lower() for pattern in passive_patterns)
                
                if found_passive and not still_passive:
                    print(f"✅ PASSIVE VOICE FIXED: Converted to active voice")
                elif found_passive and still_passive:
                    print(f"⚠️ PASSIVE VOICE REMAINING: Still contains passive construction")
                else:
                    print(f"ℹ️ OTHER IMPROVEMENT: Non-passive voice enhancement")
                    
            else:
                print(f"⚠️ NO CHANGE: Same as original")
            
            # Check conciseness
            if suggestion_words <= original_words + 3:
                print(f"✅ CONCISE: Appropriate length")
            else:
                print(f"❌ TOO VERBOSE: {suggestion_words - original_words} extra words")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 FALLBACK RULE TEST COMPLETE")

if __name__ == "__main__":
    test_fallback_rules()