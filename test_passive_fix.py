#!/usr/bin/env python3
"""
Test the improved passive voice handling for "Tags are only defined for sensors"
"""
import sys
sys.path.append('app')

from app.services.enrichment import _create_deterministic_rewrite

def test_specific_case():
    print("🧪 Testing Improved Passive Voice Detection")
    print("=" * 50)
    
    # The exact case from the user
    feedback_text = "Avoid passive voice in sentence: 'Tags are only defined for sensors.'"
    sentence_context = "Tags are only defined for sensors."
    
    print(f"📝 Original: {sentence_context}")
    print(f"⚠️  Issue: {feedback_text}")
    
    result = _create_deterministic_rewrite(feedback_text, sentence_context)
    
    print(f"✨ Improved Result: {result}")
    
    if result == f"Improve clarity: {sentence_context}":
        print("❌ STILL USING GENERIC FALLBACK - Fix didn't work")
    elif result == sentence_context:
        print("❌ NO CHANGE MADE - Pattern didn't match")
    elif "The system defines" in result:
        print("✅ SUCCESS - Converted to active voice!")
    else:
        print(f"⚠️  DIFFERENT APPROACH - Analyze: {result}")

if __name__ == "__main__":
    test_specific_case()
