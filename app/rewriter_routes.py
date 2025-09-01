"""
Flask routes for the intelligent document rewriter
Provides API endpoints for document rewriting without changing the existing UI
"""

from flask import Blueprint, request, jsonify
import logging
import time
from .rewriter.ollama_rewriter import get_rewriter

logger = logging.getLogger(__name__)

# Create rewriter blueprint
rewriter_bp = Blueprint('rewriter', __name__, url_prefix='/api/rewriter')

@rewriter_bp.route('/status', methods=['GET'])
def rewriter_status():
    """Check if the rewriter service is available."""
    try:
        rewriter = get_rewriter()
        
        # Test with a simple sentence
        test_result = rewriter.rewrite_sentence("This is a test.", mode="clarity")
        
        return jsonify({
            "status": "available",
            "models": rewriter.models,
            "api_url": rewriter.api_url,
            "test_passed": test_result.get("success", False),
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Rewriter status check failed: {e}")
        return jsonify({
            "status": "unavailable",
            "error": str(e),
            "timestamp": time.time()
        }), 503

@rewriter_bp.route('/rewrite', methods=['POST'])
def rewrite_document():
    """Rewrite document content for improved readability and clarity."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        content = data.get('content')
        if not content:
            return jsonify({
                "success": False,
                "error": "No content provided"
            }), 400
        
        mode = data.get('mode', 'balanced')  # balanced, clarity, simplicity
        if mode not in ['balanced', 'clarity', 'simplicity']:
            return jsonify({
                "success": False,
                "error": "Invalid mode. Use: balanced, clarity, or simplicity"
            }), 400
        
        # Get rewriter and process the content
        rewriter = get_rewriter()
        result = rewriter.rewrite_document(content, mode)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in document rewriting endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@rewriter_bp.route('/rewrite-sentence', methods=['POST'])
def rewrite_sentence():
    """Rewrite a single sentence for improved clarity."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        sentence = data.get('sentence')
        if not sentence:
            return jsonify({
                "success": False,
                "error": "No sentence provided"
            }), 400
        
        mode = data.get('mode', 'clarity')
        if mode not in ['balanced', 'clarity', 'simplicity']:
            return jsonify({
                "success": False,
                "error": "Invalid mode. Use: balanced, clarity, or simplicity"
            }), 400
        
        # Get rewriter and process the sentence
        rewriter = get_rewriter()
        result = rewriter.rewrite_sentence(sentence, mode)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in sentence rewriting endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@rewriter_bp.route('/readability', methods=['POST'])
def calculate_readability():
    """Calculate readability scores for text without rewriting."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        text = data.get('text')
        if not text:
            return jsonify({
                "success": False,
                "error": "No text provided"
            }), 400
        
        # Get rewriter and calculate scores
        rewriter = get_rewriter()
        scores = rewriter.calculate_readability(text)
        
        return jsonify({
            "success": True,
            "text_length": len(text),
            "word_count": len(text.split()),
            "scores": scores
        })
        
    except Exception as e:
        logger.error(f"Error calculating readability: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@rewriter_bp.route('/modes', methods=['GET'])
def get_rewriting_modes():
    """Get available rewriting modes and their descriptions."""
    return jsonify({
        "modes": {
            "balanced": {
                "name": "Balanced",
                "description": "Improves readability while maintaining professionalism",
                "recommended_for": "Business documents, reports, general content",
                "passes": 2
            },
            "clarity": {
                "name": "Clarity Focus",
                "description": "Maximizes clarity and removes ambiguity", 
                "recommended_for": "Technical documentation, instructions, complex content",
                "passes": 1
            },
            "simplicity": {
                "name": "Plain Language",
                "description": "Simplifies language for broader accessibility",
                "recommended_for": "Public communications, educational content, user guides",
                "passes": 1
            }
        },
        "default_mode": "balanced"
    })

@rewriter_bp.route('/config', methods=['GET'])
def get_rewriter_config():
    """Get current rewriter configuration."""
    try:
        rewriter = get_rewriter()
        return jsonify({
            "config": {
                "api_url": rewriter.api_url,
                "models": rewriter.models,
                "timeouts": rewriter.timeouts
            }
        })
    except Exception as e:
        logger.error(f"Error getting rewriter config: {e}")
        return jsonify({
            "error": str(e)
        }), 500

# Health check endpoint
@rewriter_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check for the rewriter service."""
    return jsonify({
        "service": "document_rewriter",
        "status": "healthy",
        "timestamp": time.time()
    })
