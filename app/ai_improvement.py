"""
LlamaIndex + ChromaDB + Ollama AI suggestion system for intelligent writing recommendations.
This module provides context-aware suggestions using local Ollama models + LlamaIndex RAG.

Features:
- Local Ollama AI for unlimited, free intelligent responses
- LlamaIndex RAG with ChromaDB for context-aware analysis
- Support for Mistral and Phi-3 models
- No API quotas or costs
- Natural language explanations
- Fallbacks when local AI unavailable

Setup:
1. Install Ollama: https://ollama.ai/
2. Pull models: ollama pull mistral OR ollama pull phi3
3. Start Ollama service: ollama serve
4. No API keys needed!
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

# Import Lightning AI system
try:
    # Use lightning-fast AI system for instant responses
    from .lightning_ai import LightningAISuggestionEngine
    LLAMAINDEX_AVAILABLE = True
    logging.info("Lightning AI system loaded successfully")
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logging.warning(f"Lightning AI system not available: {e}")
    LightningAISuggestionEngine = None

logger = logging.getLogger(__name__)

class LlamaIndexAISuggestionEngine:
    """
    AI suggestion engine using local Ollama + LlamaIndex RAG.
    Unlimited, free AI suggestions without API quotas.
    """
    
    def __init__(self):
        self.llamaindex_available = LLAMAINDEX_AVAILABLE
        self.llamaindex_engine = None
        
        if self.llamaindex_available and LightningAISuggestionEngine:
            try:
                # Initialize the lightning-fast AI engine
                self.llamaindex_engine = LightningAISuggestionEngine()
                logger.info(f"Lightning AI engine initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Lightning engine: {e}")
                self.llamaindex_available = False
        
        logger.info(f"LlamaIndex AI Suggestion Engine initialized. LlamaIndex available: {self.llamaindex_available}")
        
    def _categorize_feedback(self, feedback_text: str) -> str:
        """Categorize feedback to help RAG system understand the issue type."""
        feedback_lower = feedback_text.lower()
        
        if "passive voice" in feedback_lower:
            return "passive_voice"
        elif "long sentence" in feedback_lower or "sentence length" in feedback_lower:
            return "long_sentence"
        elif "modal verb" in feedback_lower:
            return "modal_verb"
        elif "clarity" in feedback_lower:
            return "clarity"
        elif "grammar" in feedback_lower:
            return "grammar"
        elif "weak word" in feedback_lower or "modifier" in feedback_lower:
            return "word_choice"
        else:
            return "general"
        
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None,
                                     document_content: str = "") -> Dict[str, Any]:
        """
        Generate AI suggestion using local Ollama + LlamaIndex RAG.
        Unlimited, free AI suggestions without API quotas.
        
        Returns:
            Dict containing suggestion, confidence, and metadata
        """
        # Safety checks for None inputs
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
        if document_content is None:
            document_content = ""
            
        try:
            # First try the Enhanced RAG system for intelligent suggestions
            try:
                from .enhanced_rag_complete import get_enhanced_suggestion
                logger.info("Attempting Enhanced RAG suggestion")
                
                rag_result = get_enhanced_suggestion(
                    issue_text=sentence_context,
                    issue_type=self._categorize_feedback(feedback_text),
                    context=document_content[:500]  # Limit context size for performance
                )
                
                if rag_result and rag_result.get('enhanced_response'):
                    logger.info("Enhanced RAG suggestion generated successfully")
                    return {
                        "suggestion": rag_result["enhanced_response"],
                        "ai_answer": f"Enhanced with RAG: {rag_result.get('method', 'unknown')}",
                        "confidence": "high",
                        "method": "enhanced_rag",
                        "model": "ollama_rag",
                        "sources": rag_result.get("knowledge_retrieved", ""),
                        "context_used": {
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "rag_query": rag_result.get("query_used", ""),
                            "processing_time": rag_result.get("processing_time", 0)
                        }
                    }
                else:
                    logger.warning("Enhanced RAG returned empty result")
                    
            except Exception as rag_error:
                logger.warning(f"Enhanced RAG failed: {rag_error}")
            
            # Fallback to Lightning AI for ultra-fast responses
            if self.llamaindex_available and self.llamaindex_engine:
                logger.info("Using Lightning AI fallback")
                ai_result = self.llamaindex_engine.generate_contextual_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context
                )
                
                if ai_result:
                    logger.info("Lightning AI suggestion generated successfully")
                    return {
                        "suggestion": ai_result["suggestion"],
                        "ai_answer": ai_result.get("ai_answer", "Using pattern-based suggestions"),
                        "confidence": ai_result.get("confidence", "medium"),
                        "method": "lightning_ai",
                        "model": "pattern_based",
                        "sources": [],
                        "context_used": {
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "fallback_reason": "Enhanced RAG unavailable"
                        }
                    }
                else:
                    logger.error("LlamaIndex AI failed to generate suggestion")
                    return {
                        "suggestion": "AI suggestion generation failed. Please check Ollama service.",
                        "ai_answer": "Unable to process request",
                        "confidence": "low",
                        "method": "ai_error",
                        "error": "AI engine returned no result"
                    }
            else:
                logger.error("LlamaIndex AI not available")
                return {
                    "suggestion": "AI service not available. Please ensure Ollama is running.",
                    "ai_answer": "AI service unavailable",
                    "confidence": "low", 
                    "method": "ai_unavailable",
                    "error": "AI engine not initialized"
                }
            
        except Exception as e:
            logger.error(f"LlamaIndex suggestion failed: {str(e)}")
            return {
                "suggestion": f"AI processing error: {str(e)}. Please check Ollama service status.",
                "ai_answer": "Error occurred during AI processing",
                "confidence": "low",
                "method": "ai_error",
                "error": str(e)
            }
# Global instance for easy use
ai_engine = LlamaIndexAISuggestionEngine()

def get_enhanced_ai_suggestion(feedback_text: str, sentence_context: str = "",
                             document_type: str = "general", 
                             writing_goals: List[str] = None,
                             document_content: str = "") -> Dict[str, Any]:
    """
    Convenience function to get LlamaIndex-enhanced AI suggestions.
    
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
