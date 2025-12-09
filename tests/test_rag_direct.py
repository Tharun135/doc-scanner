import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testing RAG system directly...")

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    
    print("🔧 Creating RAG instance...")
    rag = DocScannerOllamaRAG()
    print(f"🔧 RAG initialized: {rag.is_initialized}")
    
    if rag.is_initialized:
        print(f"🔧 Using model: {rag.model}")
        
        print("🔧 Testing suggestion generation...")
        result = rag.get_rag_suggestion(
            feedback_text="Check use of adverb: 'precisely'",
            sentence_context="You can precisely extract the necessary information from designated PLCs.",
            document_type="technical"
        )
        
        print(f"🔧 Result: {result}")
    else:
        print("🔧 RAG not initialized")
        
except Exception as e:
    print(f"🔧 Error: {e}")
    import traceback
    traceback.print_exc()
