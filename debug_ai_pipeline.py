#!/usr/bin/env python3

"""
Debug script to trace exactly what happens with the AI suggestion pipeline.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_ai_pipeline():
    """Debug the AI suggestion pipeline to understand the flow."""
    
    from app.ai_improvement import ai_engine
    from app.llamaindex_ai import get_ai_suggestion
    
    # Your exact case
    feedback_text = "Avoid using 'above' to refer to previous content; use specific references."
    sentence_context = "Common Configurator creates a JSON configuration file that is identical to the second configuration mentioned above."
    
    print("🔍 DEBUGGING AI PIPELINE")
    print("=" * 60)
    print(f"📝 Feedback: {feedback_text}")
    print(f"📝 Original: {sentence_context}")
    print()
    
    # Test LlamaIndex availability
    print(f"🔧 LlamaIndex Available: {ai_engine.llamaindex_available}")
    
    # Try direct LlamaIndex call
    print("\n🔧 Testing get_ai_suggestion directly:")
    try:
        ai_result = get_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical",
            document_content=""
        )
        print(f"   Result: {ai_result}")
        print(f"   Type: {type(ai_result)}")
        if ai_result:
            print(f"   Keys: {ai_result.keys() if isinstance(ai_result, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test smart fallback directly
    print("\n🔧 Testing generate_smart_fallback directly:")
    try:
        fallback_result = ai_engine.generate_smart_fallback(feedback_text, sentence_context)
        print(f"   Result: {fallback_result}")
        print(f"   Type: {type(fallback_result)}")
        if fallback_result:
            print(f"   Keys: {fallback_result.keys() if isinstance(fallback_result, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test full pipeline
    print("\n🔧 Testing generate_contextual_suggestion:")
    try:
        full_result = ai_engine.generate_contextual_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical"
        )
        print(f"   Result: {full_result}")
        print(f"   Type: {type(full_result)}")
        if full_result:
            print(f"   Keys: {full_result.keys() if isinstance(full_result, dict) else 'Not a dict'}")
            if 'suggestion' in full_result:
                print(f"   Suggestion: {full_result['suggestion']}")
                print(f"   Method: {full_result.get('method', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_ai_pipeline()
