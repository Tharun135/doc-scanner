"""
Google Gemini AI suggestion system for intelligent writing recommendations.
This module provides context-aware suggestions using Google Gemini + LangChain RAG.

Features:
- Real Google Gemini AI for intelligent responses
- Context-aware writing analysis
- Natural language explanations
- Minimal fallbacks when API unavailable

Setup:
1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to .env file: GOOGLE_API_KEY=your_key_here
3. Run test: python test_gemini_integration.py
"""

import json
import re
import logging
import os
from typing import Dict, List, Optional, Any

# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available - environment variables must be set manually")

# Import RAG system (now the primary AI provider)
try:
    from .rag_system import get_rag_suggestion
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logging.warning("RAG system not available - falling back to rule-based suggestions only")

logger = logging.getLogger(__name__)

class GeminiAISuggestionEngine:
    """
    AI suggestion engine using Google Gemini + LangChain RAG primarily.
    Minimal fallbacks only when Gemini is unavailable.
    """
    
    def __init__(self):
        self.rag_available = RAG_AVAILABLE
        logger.info(f"Gemini AI Suggestion Engine initialized. RAG available: {self.rag_available}")
        
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None,
                                     document_content: str = "") -> Dict[str, Any]:
        """
        Generate AI suggestion using Gemini + RAG primarily.
        Minimal fallbacks only when Gemini is unavailable.
        
        Returns:
            Dict containing suggestion, confidence, and metadata
        """
        try:
            # Primary method: Use Gemini RAG for solution generation
            if self.rag_available:
                logger.info("Using Gemini RAG for solution generation")
                rag_result = get_rag_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context,
                    document_type=document_type,
                    document_content=document_content
                )
                
                if rag_result:
                    logger.info("Gemini RAG suggestion generated successfully")
                    return {
                        "suggestion": rag_result["suggestion"],
                        "gemini_answer": rag_result.get("gemini_answer", ""),
                        "confidence": rag_result.get("confidence", "high"),
                        "method": "gemini_rag",
                        "sources": rag_result.get("sources", []),
                        "context_used": {
                            **rag_result.get("context_used", {}),
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "primary_ai": "gemini",
                            "issue_detection": "rule_based"
                        }
                    }
                else:
                    logger.warning("Gemini RAG returned no result, using minimal fallback")
            else:
                logger.warning("Gemini RAG not available, using minimal fallback")
            
            # Minimal fallback: Basic response when Gemini is unavailable
            return self.generate_minimal_fallback(feedback_text, sentence_context)
            
        except Exception as e:
            logger.error(f"Gemini suggestion failed: {str(e)}")
            # Fall back to minimal response
            return self.generate_minimal_fallback(feedback_text, sentence_context)
    
    def generate_minimal_fallback(self, feedback_text: str, 
                                sentence_context: str = "") -> Dict[str, Any]:
        """
        Generate minimal fallback when Gemini is unavailable.
        Simple, basic responses only.
        """
        return {
            "suggestion": f"Writing issue detected: {feedback_text}. Please review and improve this text for clarity, grammar, and style.",
            "gemini_answer": f"Review the text and address: {feedback_text}",
            "confidence": "low",
            "method": "minimal_fallback",
            "note": "Gemini AI unavailable - please set GOOGLE_API_KEY in .env file"
        }

# Global instance for easy use
ai_engine = GeminiAISuggestionEngine()

def get_enhanced_ai_suggestion(feedback_text: str, sentence_context: str = "",
                             document_type: str = "general", 
                             writing_goals: List[str] = None,
                             document_content: str = "") -> Dict[str, Any]:
    """
    Convenience function to get Gemini-enhanced AI suggestions.
    
    Args:
        feedback_text: The feedback or issue identified by rules
        sentence_context: The actual sentence or text
        document_type: Type of document (technical, marketing, academic, etc.)
        writing_goals: List of writing goals (clarity, conciseness, etc.)
        document_content: Full document content for RAG context (optional)
    
    Returns:
        Dictionary with suggestion and metadata
    """
    return ai_engine.generate_contextual_suggestion(
        feedback_text, sentence_context, document_type, writing_goals, document_content
    )
