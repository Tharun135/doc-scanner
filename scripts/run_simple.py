"""
Simplified Flask startup script that focuses on RAG functionality
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for lazy loading
rag_system = None
ai_engine = None

def load_rag_system():
    """Lazy load RAG system when first needed"""
    global rag_system
    if rag_system is None:
        try:
            logger.info("Loading RAG system...")
            from scripts.rag_system import get_rag_suggestion
            rag_system = get_rag_suggestion
            logger.info("✅ RAG system loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load RAG system: {e}")
            rag_system = False
    return rag_system if rag_system is not False else None

def load_ai_engine():
    """Lazy load AI engine when first needed"""
    global ai_engine
    if ai_engine is None:
        try:
            logger.info("Loading AI engine...")
            from app.ai_improvement import AISuggestionEngine
            ai_engine = AISuggestionEngine()
            logger.info("✅ AI engine loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load AI engine: {e}")
            ai_engine = False
    return ai_engine if ai_engine is not False else None

@app.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():
    """AI suggestion endpoint with lazy loading"""
    logger.info("🔧 AI suggestion endpoint called")
    
    try:
        data = request.get_json()
        feedback_text = data.get('feedback')
        sentence_context = data.get('sentence', '')
        document_type = data.get('document_type', 'general')
        option_number = data.get('option_number', 1)
        
        logger.info(f"Request: feedback='{feedback_text[:50]}', sentence='{sentence_context[:50]}'")
        
        if not feedback_text:
            return jsonify({"error": "No feedback provided"}), 400
        
        # Try loading AI engine first
        engine = load_ai_engine()
        if engine:
            logger.info("🔧 Using AI engine")
            
            # Create issue object to trigger RAG enrichment
            issue = {
                'message': feedback_text,
                'context': sentence_context,
                'issue_type': 'Writing Issue'  # Generic type, could be inferred
            }
            
            result = engine.generate_contextual_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                option_number=option_number,
                issue=issue  # Pass issue to trigger RAG enrichment
            )
            logger.info(f"🔧 AI engine result: method={result.get('method')}")
            return jsonify(result)
        
        # Fallback to direct RAG
        rag_func = load_rag_system()
        if rag_func:
            logger.info("🔧 Using direct RAG")
            result = rag_func(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                document_content=""
            )
            if result:
                return jsonify({
                    "suggestion": result["suggestion"],
                    "ai_answer": result.get("ai_answer", ""),
                    "confidence": result.get("confidence", "high"),
                    "method": "direct_rag"
                })
        
        # Final fallback
        logger.info("🔧 Using basic fallback")
        return jsonify({
            "suggestion": f"Consider revising: {sentence_context}",
            "ai_answer": f"Review the text and address: {feedback_text}",
            "confidence": "low",
            "method": "basic_fallback"
        })
        
    except Exception as e:
        logger.error(f"🔧 Exception in AI suggestion: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "rag_loaded": rag_system is not None})

if __name__ == '__main__':
    print("🚀 Starting simplified DocScanner Flask server...")
    print("📍 AI suggestions available at: http://localhost:5001/ai_suggestion")
    print("🏥 Health check at: http://localhost:5001/health")
    
    try:
        app.run(
            host='127.0.0.1', 
            port=5001, 
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
