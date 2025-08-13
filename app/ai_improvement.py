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
            # Use Lightning AI for all suggestions - ultra-fast responses
            if self.llamaindex_available and self.llamaindex_engine:
                logger.info("Using Lightning AI for solution generation")
                ai_result = self.llamaindex_engine.generate_contextual_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context
                )
                
                if ai_result:
                    logger.info("LlamaIndex AI suggestion generated successfully")
                    return {
                        "suggestion": ai_result["suggestion"],
                        "ai_answer": ai_result.get("ai_answer", ""),
                        "confidence": ai_result.get("confidence", "high"),
                        "method": "llamaindex_ai",
                        "model": ai_result.get("model", "ollama_local"),
                        "sources": ai_result.get("sources", []),
                        "context_used": {
                            **ai_result.get("context_used", {}),
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "primary_ai": "ollama_local",
                            "issue_detection": "rule_based"
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
