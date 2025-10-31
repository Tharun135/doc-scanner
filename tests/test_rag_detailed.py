#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🔍 Detailed RAG Testing")
print("=" * 40)

try:
    from app.rules.passive_voice import RAG_HELPER_AVAILABLE, check
    print(f"RAG_HELPER_AVAILABLE in passive_voice.py: {RAG_HELPER_AVAILABLE}")
    
    if RAG_HELPER_AVAILABLE:
        print("✅ RAG helper is available in passive voice rule")
        
        # Test with a clear passive voice sentence
        test_content = '<p>The document was written by John yesterday.</p>'
        print(f"\nTesting content: {test_content}")
        
        try:
            results = check(test_content)
            print(f"📊 Results: {len(results)} suggestions")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result}")
                
        except Exception as e:
            print(f"❌ Error during check: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ RAG helper not available in passive voice rule")
        
except Exception as e:
    print(f"❌ Error importing: {e}")
    import traceback
    traceback.print_exc()

# Test RAG system directly
print(f"\n🧪 Testing RAG System Directly:")
try:
    sys.path.append('scripts')
    from rag_system import get_rag_suggestion
    
    result = get_rag_suggestion(
        feedback_text="Passive voice detected: 'was written' - convert to active voice",
        sentence_context="The document was written by John yesterday.",
        document_type="technical"
    )
    
    if result:
        print("✅ Direct RAG call successful!")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'No suggestion')[:200]}...")
    else:
        print("⚠️ Direct RAG call returned None")
        
except Exception as e:
    print(f"❌ Direct RAG error: {e}")
    import traceback
    traceback.print_exc()
