"""
Test the improved RAG system with the user's specific examples
"""
import sys
sys.path.append('.')
sys.path.append('scripts')

print("🔧 Testing improved RAG system with user examples...")

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    
    rag = DocScannerOllamaRAG()
    
    # Test case 1: Click on -> click
    print("\n📝 Test 1: Click on -> click")
    result1 = rag.get_rag_suggestion(
        feedback_text="Use 'click' instead of 'click on'",
        sentence_context="Click on the Dashboard icon and select any configured asset.",
        document_type="technical"
    )
    
    if result1:
        print(f"✅ Original: Click on the Dashboard icon and select any configured asset.")
        print(f"✅ Fixed:    {result1['suggestion']}")
        if "click on" not in result1['suggestion'].lower():
            print("🎉 SUCCESS: 'click on' was removed!")
        else:
            print("❌ FAILED: Still contains 'click on'")
    
    # Test case 2: Passive voice
    print("\n📝 Test 2: Passive voice fix")
    result2 = rag.get_rag_suggestion(
        feedback_text="Avoid passive voice in sentence",
        sentence_context="The Time, Description, and Comments columns are fixed and cannot be removed.",
        document_type="technical"
    )
    
    if result2:
        print(f"✅ Original: The Time, Description, and Comments columns are fixed and cannot be removed.")
        print(f"✅ Fixed:    {result2['suggestion']}")
        if "Consider Revising" not in result2['suggestion']:
            print("🎉 SUCCESS: No generic 'Consider Revising' response!")
        else:
            print("❌ FAILED: Still shows generic response")
    
    print(f"\n📊 Summary:")
    print(f"Test 1 Result: {'✅ PASS' if result1 and 'click on' not in result1['suggestion'].lower() else '❌ FAIL'}")
    print(f"Test 2 Result: {'✅ PASS' if result2 and 'Consider Revising' not in result2['suggestion'] else '❌ FAIL'}")

except Exception as e:
    print(f"❌ Error testing: {e}")
    import traceback
    traceback.print_exc()
