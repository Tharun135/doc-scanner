#!/usr/bin/env python3
"""
Quick test for the non-technical term fix
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from ai_improvement import GeminiAISuggestionEngine
    
    def test_no_technical_terms():
        """Test that we don't create new technical terms."""
        
        ai_engine = GeminiAISuggestionEngine()
        
        feedback_text = "Convert to active voice: 'The Docker daemon does not generate logs when no applications are running.'"
        sentence_context = "Docker logs are not generated when there are no active applications."
        
        print("🔍 Testing No Technical Terms Fix")
        print("=" * 50)
        print(f"Original: {sentence_context}")
        print("-" * 30)
        
        # Test individual conversion functions
        fix1 = ai_engine._fix_passive_voice(sentence_context)
        fix2 = ai_engine._alternative_active_voice(sentence_context)
        fix3 = ai_engine._direct_action_voice(sentence_context)
        
        print(f"Fix 1: {fix1}")
        print(f"Fix 2: {fix2}")
        print(f"Fix 3: {fix3}")
        
        # Check if we're avoiding "Docker daemon"
        if "Docker daemon" in fix1:
            print("❌ ISSUE: Still using 'Docker daemon' technical term")
        else:
            print("✅ GOOD: No 'Docker daemon' technical term")
        
        # Check if we're using simpler language
        if "Docker does not generate" in fix1:
            print("✅ GOOD: Using simpler 'Docker does not generate'")
        else:
            print(f"ℹ️  INFO: Using alternative phrasing: {fix1}")
        
        print(f"\n🎯 Results:")
        print(f"1. {fix1}")
        print(f"2. {fix2}")
        print(f"3. {fix3}")

    if __name__ == "__main__":
        test_no_technical_terms()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
