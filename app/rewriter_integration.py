"""
Integration patch for adding rewriter functionality to existing doc-scanner endpoints
This module provides decorators and utilities to enhance existing functionality without breaking changes
"""

import logging
from functools import wraps
from flask import request, jsonify
from typing import Dict, Any

logger = logging.getLogger(__name__)

def enhance_ai_suggestion_response(original_function):
    """
    Decorator to enhance the ai_suggestion endpoint with rewriting capabilities.
    This is applied to the existing ai_suggestion route to add rewriting without changing the core logic.
    """
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        try:
            # Get the original result
            original_response = original_function(*args, **kwargs)
            
            # Check if we should enhance with rewriting
            request_data = request.get_json() or {}
            enable_rewriting = request_data.get('enable_rewriting', False)
            
            # If rewriting is not requested, return original response
            if not enable_rewriting:
                return original_response
            
            # Extract data from the original response for enhancement
            if hasattr(original_response, 'get_json'):
                response_data = original_response.get_json()
            elif isinstance(original_response, tuple) and len(original_response) >= 1:
                response_data = original_response[0].get_json() if hasattr(original_response[0], 'get_json') else {}
            else:
                response_data = {}
            
            if not response_data:
                return original_response
            
            # Enhance with rewriting
            feedback_text = request_data.get('feedback', '')
            sentence_context = request_data.get('sentence', '')
            
            if feedback_text and sentence_context:
                from .enhanced_suggestions import get_enhanced_suggestion_system
                
                enhanced_system = get_enhanced_suggestion_system()
                enhanced_result = enhanced_system.enhance_suggestion_with_rewriting(
                    response_data, feedback_text, sentence_context
                )
                
                # Return enhanced response
                return jsonify(enhanced_result)
            
            return original_response
            
        except Exception as e:
            logger.error(f"Error in rewriter enhancement: {e}")
            # Return original response if enhancement fails
            return original_function(*args, **kwargs)
    
    return wrapper

def add_rewriter_endpoints_to_blueprint(blueprint):
    """
    Add rewriter endpoints to an existing Flask blueprint without modifying the original blueprint.
    This allows us to extend functionality without changing existing code.
    """
    
    @blueprint.route('/rewrite-suggestion', methods=['POST'])
    def get_rewrite_suggestion():
        """New endpoint that provides rewriting suggestions for any text."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No JSON data provided"}), 400
            
            text = data.get('text') or data.get('sentence', '')
            mode = data.get('mode', 'balanced')
            
            if not text:
                return jsonify({"success": False, "error": "No text provided"}), 400
            
            from .enhanced_suggestions import get_enhanced_suggestion_system
            enhanced_system = get_enhanced_suggestion_system()
            
            # Use the rewriter directly
            result = enhanced_system.rewriter.rewrite_sentence(text, mode)
            
            # Format as suggestion response (compatible with existing UI expectations)
            if result.get("success"):
                return jsonify({
                    "suggestion": result.get("rewritten", text),
                    "ai_answer": f"AI-enhanced rewrite (mode: {mode})",
                    "confidence": "high",
                    "method": "ollama_rewriter",
                    "rewriting": {
                        "available": True,
                        "mode_used": mode,
                        "readability_scores": result.get("scores", {})
                    },
                    "sources": [{
                        "rule_id": "rewriter_v1",
                        "title": f"AI Rewriting ({mode} mode)",
                        "similarity": 0.95
                    }]
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "Rewriting failed")
                }), 500
                
        except Exception as e:
            logger.error(f"Error in rewrite suggestion endpoint: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @blueprint.route('/readability-analysis', methods=['POST'])
    def get_readability_analysis():
        """New endpoint for readability analysis."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No JSON data provided"}), 400
            
            text = data.get('text', '')
            if not text:
                return jsonify({"success": False, "error": "No text provided"}), 400
            
            from .enhanced_suggestions import get_readability_analysis
            result = get_readability_analysis(text)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in readability analysis endpoint: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    logger.info("Added rewriter endpoints to blueprint")

def create_rewriter_config():
    """Create configuration for the rewriter integration."""
    return {
        "rewriter": {
            "enabled": True,
            "default_mode": "balanced",
            "auto_enhance_suggestions": False,  # Set to True to automatically enhance all suggestions
            "endpoints": {
                "rewrite_suggestion": "/rewrite-suggestion",
                "readability_analysis": "/readability-analysis"
            }
        }
    }
