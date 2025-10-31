"""
Test the specific adverb case that's failing
"""
import sys
sys.path.append('.')
sys.path.append('scripts')

print("🔧 Testing adverb case that's failing...")

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    
    rag = DocScannerOllamaRAG()
    
    # Test the exact case the user reported
    print("\n📝 Test: Adverb 'efficiently'")
    result = rag.get_rag_suggestion(
        feedback_text="Check use of adverb: 'efficiently' in sentence 'The Logbook offers a detailed record of diagnostic and alarm events, helping you in tracking performance and identifying recurring issues efficiently.'",
        sentence_context="The Logbook offers a detailed record of diagnostic and alarm events, helping you in tracking performance and identifying recurring issues efficiently.",
        document_type="technical"
    )
    
    if result:
        print(f"✅ Original:   {result.get('original', 'N/A')}")
        print(f"✅ Suggestion: {result['suggestion']}")
        print(f"✅ Method:     {result.get('method', 'unknown')}")
        
        # Check if it's the same generic response
        if "Consider Revising For Better Clarity:" in result['suggestion']:
            print("❌ FAILED: Still showing generic response")
        else:
            print("🎉 SUCCESS: Intelligent suggestion provided!")
            
        # Check if 'efficiently' was addressed
        if "efficiently" not in result['suggestion']:
            print("🎉 SUCCESS: 'efficiently' was removed/addressed!")
        else:
            print("ℹ️ 'efficiently' still present in suggestion")
    else:
        print("❌ No result returned")

except Exception as e:
    print(f"❌ Error testing: {e}")
    import traceback
    traceback.print_exc()
