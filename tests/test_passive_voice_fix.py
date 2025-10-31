#!/usr/bin/env python3
"""
Test the passive voice fix for the AI suggestion system.
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from ai_improvement import GeminiAISuggestionEngine
    
    def test_passive_voice_fix():
        """Test the specific passive voice issue that was reported."""
        
        # Create the AI suggestion engine
        ai_engine = GeminiAISuggestionEngine()
        
        # Test case from the user's report
        feedback_text = "Convert to active voice: 'The Docker daemon does not generate logs when no applications are running.'"
        sentence_context = "Docker logs are not generated when there are no active applications."
        
        print("🔍 Testing Passive Voice Fix")
        print("=" * 50)
        print(f"Feedback: {feedback_text}")
        print(f"Original sentence: {sentence_context}")
        print("-" * 50)
        
        # Test the minimal fallback method (which is what's being used when RAG fails)
        result = ai_engine.generate_minimal_fallback(feedback_text, sentence_context)
        
        print("✅ AI Suggestion Result:")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 'unknown')}")
        print("Suggestion:")
        print(result.get('suggestion', 'No suggestion provided'))
        
        # Check if the suggestion contains actual rewrites instead of the original sentence
        suggestion = result.get('suggestion', '')
        if "Docker logs are not generated when there are no active applications" in suggestion:
            print("\n❌ ISSUE: The suggestion still contains the original sentence!")
        else:
            print("\n✅ SUCCESS: The suggestion provides actual rewrites!")
        
        # Test individual rewrite functions
        print("\n🔧 Testing Individual Rewrite Functions:")
        print("-" * 50)
        
        # Test _fix_passive_voice
        fix1 = ai_engine._fix_passive_voice(sentence_context)
        print(f"_fix_passive_voice: {fix1}")
        
        # Test _alternative_active_voice
        fix2 = ai_engine._alternative_active_voice(sentence_context)
        print(f"_alternative_active_voice: {fix2}")
        
        # Test _direct_action_voice
        fix3 = ai_engine._direct_action_voice(sentence_context)
        print(f"_direct_action_voice: {fix3}")
        
        # Check if any of the functions returned something different
        if fix1 != sentence_context:
            print(f"✅ _fix_passive_voice successfully converted the sentence")
        else:
            print(f"❌ _fix_passive_voice returned original sentence")
            
        if fix2 != sentence_context:
            print(f"✅ _alternative_active_voice successfully converted the sentence")
        else:
            print(f"❌ _alternative_active_voice returned original sentence")
            
        if fix3 != sentence_context:
            print(f"✅ _direct_action_voice successfully converted the sentence")
        else:
            print(f"❌ _direct_action_voice returned original sentence")
        
        print("\n🎯 Expected vs Actual:")
        print(f"Expected active voice: 'The Docker daemon does not generate logs when no applications are running.'")
        print(f"Our conversion 1: '{fix1}'")
        print(f"Our conversion 2: '{fix2}'")
        print(f"Our conversion 3: '{fix3}'")
        
    if __name__ == "__main__":
        test_passive_voice_fix()
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the doc-scanner directory")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
