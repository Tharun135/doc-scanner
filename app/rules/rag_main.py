"""
RAG Helper - Main Interface
Provides RAG-based writing suggestions with fallback to simplified system.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_rag_suggestion(issue_text: str, sentence_context: str, category: str = "general") -> Dict[str, Any]:
    """
    Main function to get RAG-based suggestions.
    Uses simplified keyword-based RAG system.
    """
    try:
        from .simplified_rag import simplified_rag
        return simplified_rag.get_rule_based_suggestion(issue_text, sentence_context, category)
    except ImportError as e:
        logger.error(f"Error importing simplified RAG: {e}")
        return _emergency_fallback(issue_text, sentence_context, category)

def is_rag_available() -> bool:
    """Check if RAG system is available."""
    try:
        from .simplified_rag import simplified_rag
        return simplified_rag.initialized
    except ImportError:
        return False

def add_writing_rule(rule: Dict[str, Any]) -> bool:
    """Add a new writing rule to the RAG system."""
    try:
        from .simplified_rag import add_writing_rule as add_rule
        return add_rule(rule)
    except ImportError:
        logger.warning("Rule addition not available")
        return False

def _emergency_fallback(issue_text: str, sentence_context: str, category: str) -> Dict[str, Any]:
    """Emergency fallback when all RAG systems fail."""
    return {
        "suggestion": f"**{issue_text.title()}**\n\nPlease review this sentence for {category} improvements.\n\n**Sentence:** \"{sentence_context}\"",
        "confidence": 0.3,
        "source": "emergency_fallback",
        "retrieved_rules": 0,
        "rule_based": False
    }
