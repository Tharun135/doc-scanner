"""
Debug what RAG is actually returning for the passive voice case
"""
import sys
sys.path.append('.')
sys.path.append('scripts')

print("🔧 Debugging RAG responses...")

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    
    rag = DocScannerOllamaRAG()
    
    # Debug the passive voice case step by step
    print("\n📝 Debug Test: Passive voice")
    original_sentence = "The Time, Description, and Comments columns are fixed and cannot be removed."
    feedback_text = "Avoid passive voice in sentence"
    
    print(f"Input sentence: {original_sentence}")
    print(f"Feedback: {feedback_text}")
    
    # Let's see what the RAG query actually returns
    result = rag.get_rag_suggestion(
        feedback_text=feedback_text,
        sentence_context=original_sentence,
        document_type="technical"
    )
    
    if result:
        print(f"\n📊 RAG Result:")
        print(f"  Suggestion: {result['suggestion']}")
        print(f"  Method: {result.get('method', 'unknown')}")
        
        # Check if it should trigger passive voice fallback
        if "columns are fixed and cannot be removed" in original_sentence.lower():
            expected = "The system fixes the Time, Description, and Comments columns and prevents their removal."
            print(f"\n✅ Expected fallback: {expected}")
            if result['suggestion'] == expected:
                print("🎉 Perfect! Fallback worked correctly!")
            else:
                print("❌ Fallback did not trigger or didn't work as expected")
    else:
        print("❌ No result returned")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
