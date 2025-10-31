import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testing RAG suggestion with user's passive voice example...")

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    
    print("🔧 Creating RAG instance...")
    rag = DocScannerOllamaRAG()
    print(f"🔧 RAG initialized: {rag.is_initialized}")
    
    if rag.is_initialized:
        print(f"🔧 Using model: {rag.model}")
        
        # Test with the exact example from the user
        print("🔧 Testing with passive voice example...")
        result = rag.get_rag_suggestion(
            feedback_text="Avoid passive voice in sentence",
            sentence_context="Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.",
            document_type="technical"
        )
        
        print("🔧 RAG Response:")
        print(f"   Suggestion: {result.get('suggestion', 'N/A')}")
        print(f"   Method: {result.get('method', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        print(f"   Raw Result: {result}")
        
        # Test what the query engine actually returns
        print("\n🔧 Testing direct query engine...")
        if rag.query_engine:
            query = f"""
            Fix this writing issue: Avoid passive voice in sentence
            
            Original sentence: "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook."
            Document type: technical
            
            Provide a complete rewrite that fixes the issue. 
            Make it clear, direct, and appropriate for technical writing.
            Give only the improved sentence, no explanation needed.
            """
            
            response = rag.query_engine.query(query)
            raw_response = str(response).strip()
            print(f"   Raw Ollama Response: '{raw_response}'")
            
            # Test the cleaning function
            cleaned = rag._clean_suggestion(raw_response, "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.")
            print(f"   Cleaned Suggestion: '{cleaned}'")
        
    else:
        print("🔧 RAG not initialized")
        
except Exception as e:
    print(f"🔧 Error: {e}")
    import traceback
    traceback.print_exc()
