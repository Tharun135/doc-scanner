"""
Minimal Flask test for AI suggestions
"""
from flask import Flask, request, jsonify
import sys
import os
sys.path.append('.')
sys.path.append('scripts')

app = Flask(__name__)

# Import RAG system
try:
    from scripts.rag_system import get_rag_suggestion
    RAG_AVAILABLE = True
    print("✅ RAG system loaded successfully")
except ImportError as e:
    RAG_AVAILABLE = False
    print(f"❌ RAG system failed to load: {e}")

@app.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():
    print("🔧 AI suggestion endpoint called")
    
    data = request.get_json()
    feedback_text = data.get('feedback')
    sentence_context = data.get('sentence', '')
    document_type = data.get('document_type', 'general')
    
    print(f"🔧 Request: feedback='{feedback_text[:50]}', sentence='{sentence_context[:50]}'")
    
    if not feedback_text:
        return jsonify({"error": "No feedback provided"}), 400
    
    try:
        if RAG_AVAILABLE:
            print("🔧 Calling RAG system...")
            result = get_rag_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                document_content=""
            )
            print(f"🔧 RAG result: {result}")
            
            if result:
                return jsonify({
                    "suggestion": result["suggestion"],
                    "ai_answer": result.get("ai_answer", ""),
                    "confidence": result.get("confidence", "high"),
                    "method": "local_rag",
                    "sources": result.get("sources", [])
                })
        
        # Fallback
        print("🔧 Using fallback suggestion")
        return jsonify({
            "suggestion": f"Consider revising: {sentence_context}",
            "ai_answer": f"Review the text and address: {feedback_text}",
            "confidence": "medium",
            "method": "smart_fallback"
        })
        
    except Exception as e:
        print(f"🔧 Exception: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting minimal Flask test server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
