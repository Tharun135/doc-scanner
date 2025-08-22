"""
RAG System Interface - DEBUG VERSION
Simple fallback to test if the loading issue is resolved.
"""

import logging
from typing import Dict, List, Optional, Any

def get_rag_suggestion(feedback_text: str, sentence_context: str, document_type: str = "general", document_content: str = "") -> Dict[str, Any]:
    """
    Get an AI suggestion - DEBUG VERSION WITH IMMEDIATE RETURN
    """
    logging.info(f"🔧 DEBUG: AI suggestion request - feedback='{feedback_text[:50]}', sentence='{sentence_context[:50]}'")
    
    # Return immediately to test if this fixes the loading issue
    result = {
        'suggestion': f"Consider improving this text: {sentence_context}",
        'confidence': 'medium',
        'method': 'debug_mode',
        'sources': []
    }
    
    logging.info(f"🔧 DEBUG: Returning suggestion with method '{result['method']}'")
    return result
