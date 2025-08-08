#!/usr/bin/env python3

"""
Test script to debug the reference fixing functions directly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import LlamaIndexAISuggestionEngine

def test_reference_functions():
    """Test the individual reference fixing functions."""
    
    ai_engine = LlamaIndexAISuggestionEngine()
    
    test_sentence = "Common Configurator creates a JSON configuration file that is identical to the second configuration mentioned above."
    
    print("🧪 TESTING REFERENCE FIXING FUNCTIONS")
    print("=" * 60)
    print(f"📝 Original: {test_sentence}")
    print()
    
    # Test each function individually
    print("🔧 Testing _fix_above_reference:")
    try:
        result1 = ai_engine._fix_above_reference(test_sentence)
        print(f"   Result: {result1}")
        print(f"   Changed: {result1 != test_sentence}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔧 Testing _alternative_reference_fix:")
    try:
        result2 = ai_engine._alternative_reference_fix(test_sentence)
        print(f"   Result: {result2}")
        print(f"   Changed: {result2 != test_sentence}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔧 Testing _specific_reference_fix:")
    try:
        result3 = ai_engine._specific_reference_fix(test_sentence)
        print(f"   Result: {result3}")
        print(f"   Changed: {result3 != test_sentence}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🔧 Testing _generate_sentence_rewrite directly:")
    try:
        feedback = "Avoid using 'above' to refer to previous content; use specific references."
        result4 = ai_engine._generate_sentence_rewrite(feedback, test_sentence)
        print(f"   Result: {result4}")
        print(f"   Contains original: {'mentioned above' in result4}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
    print("\n🔧 Testing generate_smart_fallback:")
    try:
        feedback = "Avoid using 'above' to refer to previous content; use specific references."
        result5 = ai_engine.generate_smart_fallback(feedback, test_sentence)
        print(f"   Result: {result5}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_reference_functions()
