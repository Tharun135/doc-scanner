#!/usr/bin/env python3
"""
Test script to verify AI responses are concise and not verbose essays.
Focus on passive voice conversion that was generating 100+ word responses.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from intelligent_ai_improvement import IntelligentAISuggestionEngine
import logging

# Set up logging to see the detailed process
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_concise_responses():
    """Test that AI responses are concise, not verbose essays."""
    
    print("🧪 TESTING CONCISE AI RESPONSES")
    print("=" * 50)
    
    # Initialize the AI improvement system
    ai_improver = IntelligentAISuggestionEngine()
    
    # Test cases that were generating verbose essays
    test_cases = [
        "The available connectors are shown.",
        "Data is displayed in the dashboard.",
        "Reports are generated automatically.",
        "The configuration settings are provided.",
        "Information is shown in the sidebar.",
        "The system shows available connectors."  # This should be simple and not need much change
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n🔍 TEST {i}: {sentence}")
        print("-" * 40)
        
        try:
            # Get the AI suggestion
            result = ai_improver.generate_contextual_suggestion(sentence, "passive voice")
            
            if result:
                suggestion = result.get('suggestion', '')
                explanation = result.get('explanation', '')
                confidence = result.get('confidence', 0)
                
                # Count words
                original_words = len(sentence.split())
                suggestion_words = len(suggestion.split())
                explanation_words = len(explanation.split())
                
                print(f"✅ ORIGINAL ({original_words} words): {sentence}")
                print(f"🔧 SUGGESTION ({suggestion_words} words): {suggestion}")
                print(f"📝 EXPLANATION ({explanation_words} words): {explanation}")
                print(f"🎯 CONFIDENCE: {confidence}")
                
                # Validate conciseness
                if suggestion_words <= original_words + 5:
                    print(f"✅ CONCISE: Suggestion is appropriately brief")
                else:
                    print(f"❌ TOO VERBOSE: Suggestion has {suggestion_words - original_words} extra words")
                
                if explanation_words <= 15:
                    print(f"✅ CONCISE EXPLANATION: Brief and clear")
                else:
                    print(f"❌ VERBOSE EXPLANATION: {explanation_words} words (should be ≤15)")
                    
            else:
                print("❌ NO SUGGESTION RETURNED")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 CONCISENESS TEST COMPLETE")

if __name__ == "__main__":
    test_concise_responses()