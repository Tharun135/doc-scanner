"""
Minimal Flask server to test document-first AI routing without full dependencies
This bypasses the sentence transformer download issues
"""

import sys
import os
sys.path.append('app')

from flask import Flask, request, jsonify
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Mock the ChromaDB and sentence transformers to avoid download issues
class MockCollection:
    def count(self):
        return 7042
    
    def query(self, query_texts, n_results=5):
        return {
            'documents': [['Mock document content about PLC configuration and automation']],
            'metadatas': [[{'source': 'technical_manual.pdf', 'page': 42}]],
            'distances': [[0.3]]
        }

class MockChromaClient:
    def get_or_create_collection(self, name):
        return MockCollection()

# Mock imports to prevent download issues
import types
mock_chromadb = types.ModuleType('chromadb')
mock_chromadb.PersistentClient = lambda path: MockChromaClient()
sys.modules['chromadb'] = mock_chromadb

# Mock sentence transformers
mock_sentence_transformers = types.ModuleType('sentence_transformers')
class MockSentenceTransformer:
    def __init__(self, model_name):
        self.model_name = model_name
    def encode(self, texts):
        return [[0.1] * 384 for _ in texts]
mock_sentence_transformers.SentenceTransformer = MockSentenceTransformer
sys.modules['sentence_transformers'] = mock_sentence_transformers

# Now import our AI systems
try:
    from app.intelligent_ai_improvement import IntelligentAISuggestionEngine
    INTELLIGENT_AI_AVAILABLE = True
    intelligent_engine = IntelligentAISuggestionEngine()
    logger.info("✅ Intelligent AI system loaded successfully")
except Exception as e:
    INTELLIGENT_AI_AVAILABLE = False
    intelligent_engine = None
    logger.error(f"❌ Failed to load intelligent AI: {e}")

try:
    from app.ai_improvement import get_enhanced_ai_suggestion
    ENHANCED_AI_AVAILABLE = True
    logger.info("✅ Enhanced AI system loaded successfully")
except Exception as e:
    ENHANCED_AI_AVAILABLE = False
    get_enhanced_ai_suggestion = None
    logger.error(f"❌ Failed to load enhanced AI: {e}")

@app.route('/ai_suggestion', methods=['POST'])
def ai_suggestion():
    """Test the document-first routing with our fix"""
    data = request.get_json() or {}
    feedback_text = data.get('feedback')
    sentence_context = data.get('sentence', '')
    document_type = data.get('document_type', 'general')
    writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
    
    logger.info(f"🔧 AI suggestion request: {feedback_text}")
    
    if not feedback_text:
        return jsonify({"error": "No feedback provided"}), 400

    try:
        # APPLY OUR ROUTING FIX: Use intelligent AI system first
        if INTELLIGENT_AI_AVAILABLE and intelligent_engine:
            logger.info("🔍 Using DOCUMENT-FIRST intelligent AI suggestion...")
            
            # Call the document-first system
            result = intelligent_engine.generate_contextual_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                writing_goals=writing_goals
            )
            
            logger.info(f"✅ Document-first result: method={result.get('method')}")
            return jsonify(result)
            
        elif ENHANCED_AI_AVAILABLE and get_enhanced_ai_suggestion:
            logger.info("⚠️ Falling back to standard enhanced AI suggestion...")
            
            result = get_enhanced_ai_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                writing_goals=writing_goals
            )
            
            logger.info(f"⚠️ Fallback result: method={result.get('method')}")
            return jsonify(result)
            
        else:
            return jsonify({
                "error": "No AI systems available",
                "method": "error",
                "confidence": "none"
            }), 500
            
    except Exception as e:
        logger.error(f"❌ AI suggestion failed: {e}")
        return jsonify({
            "error": str(e),
            "method": "error",
            "confidence": "none"
        }), 500

@app.route('/test_status', methods=['GET'])
def test_status():
    """Check which AI systems are available"""
    return jsonify({
        "intelligent_ai_available": INTELLIGENT_AI_AVAILABLE,
        "enhanced_ai_available": ENHANCED_AI_AVAILABLE,
        "mock_documents": 7042,
        "routing_fix_applied": True
    })

if __name__ == '__main__':
    print("🚀 Starting minimal test server for document-first AI routing...")
    print("✅ This server bypasses download issues and tests our routing fix")
    print("🔧 Access: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)