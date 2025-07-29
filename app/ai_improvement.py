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
        Generate intelligent fallback when Gemini is unavailable.
        Provides complete sentence rewrites using rule-based logic.
        """
        if sentence_context:
            # Generate complete sentence rewrites based on common issues
            suggestion = self._generate_sentence_rewrite(feedback_text, sentence_context)
        else:
            suggestion = f"Writing issue detected: {feedback_text}. Please review and improve this text for clarity, grammar, and style."
        
        return {
            "suggestion": suggestion,
            "gemini_answer": f"Review the text and address: {feedback_text}",
            "confidence": "medium",
            "method": "smart_fallback",
            "note": "Using smart fallback - Gemini quota exceeded or unavailable"
        }
    
    def _generate_sentence_rewrite(self, feedback_text: str, sentence_context: str) -> str:
        """Generate complete sentence rewrites using rule-based logic."""
        feedback_lower = feedback_text.lower()
        
        # Passive voice fixes
        if "passive voice" in feedback_lower:
            rewrites = [
                self._fix_passive_voice(sentence_context),
                self._alternative_active_voice(sentence_context),
                self._direct_action_voice(sentence_context)
            ]
        # First person fixes
        elif "first person" in feedback_lower or "we" in feedback_lower:
            rewrites = [
                sentence_context.replace("We recommend", "Consider").replace("we recommend", "consider"),
                sentence_context.replace("We suggest", "The recommended approach is").replace("we suggest", "the recommended approach is"),
                sentence_context.replace("We believe", "This feature provides").replace("we believe", "this feature provides")
            ]
        # Modal verb fixes
        elif "modal verb" in feedback_lower and "may" in feedback_lower:
            rewrites = [
                sentence_context.replace("You may now click", "Click").replace("you may now click", "click"),
                sentence_context.replace("You may", "You can").replace("you may", "you can"),
                sentence_context.replace("You may now", "To").replace("you may now", "to")
            ]
        # Long sentence fixes
        elif "long" in feedback_lower or "sentence too long" in feedback_lower:
            rewrites = self._split_long_sentence(sentence_context)
        else:
            # Generic improvements
            rewrites = [
                sentence_context.strip() + " (Improved version needed)",
                "Consider revising: " + sentence_context.strip(),
                "Alternative: " + sentence_context.strip()
            ]
        
        # Filter out empty or identical rewrites
        valid_rewrites = [r for r in rewrites if r and r.strip() != sentence_context.strip()]
        
        if not valid_rewrites:
            valid_rewrites = [
                f"Rewrite needed: {sentence_context}",
                f"Improve this sentence: {sentence_context}",
                f"Consider alternatives for: {sentence_context}"
            ]
        
        # Format as options
        options = []
        for i, rewrite in enumerate(valid_rewrites[:3], 1):
            options.append(f"OPTION {i}: {rewrite.strip()}")
        
        why_text = f"WHY: Addresses {feedback_text.lower()} for better technical writing."
        
        return "\n".join(options) + f"\n{why_text}"
    
    def _fix_passive_voice(self, sentence: str) -> str:
        """Basic passive voice to active voice conversion."""
        # Handle common passive patterns
        sentence_lower = sentence.lower()
        
        if "was reviewed by the team" in sentence_lower:
            return sentence.replace("was reviewed by the team", "the team reviewed")
        elif "was written by" in sentence_lower:
            return sentence.replace("was written by", "").replace("The document ", "").strip() + " wrote the document"
        elif "was created by" in sentence_lower:
            return sentence.replace("was created by", "").replace("The ", "").strip() + " created this"
        elif "changes were made" in sentence_lower:
            return sentence.replace("changes were made", "the team made changes")
        elif "was designed by" in sentence_lower:
            return sentence.replace("was designed by", "").strip() + " designed this"
        else:
            # Generic active voice conversion
            return sentence.replace("was ", "").replace("were ", "").replace("The ", "This ")
    
    def _alternative_active_voice(self, sentence: str) -> str:
        """Generate alternative active voice version."""
        # Remove passive constructions and make more direct
        result = sentence
        if "The document was" in sentence:
            result = sentence.replace("The document was carefully reviewed by the team", "The team carefully reviewed the document")
        elif "several changes were made" in sentence.lower():
            result = sentence.replace("several changes were made", "the team made several changes")
        
        return result if result != sentence else f"Direct version: {sentence.replace('was ', '').replace('were ', '')}"
    
    def _direct_action_voice(self, sentence: str) -> str:
        """Generate direct action version."""
        # Create imperative or direct statements
        if "The document was" in sentence:
            return "Review the document and make necessary changes for clarity."
        elif "changes were made" in sentence.lower():
            return "Make changes to improve document clarity."
        else:
            return f"Use active voice: {sentence.replace(' was ', ' ').replace(' were ', ' ')}"
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split long sentences into shorter ones."""
        # Simple sentence splitting on common conjunctions
        if " and " in sentence:
            parts = sentence.split(" and ", 1)
            return [
                parts[0].strip() + ".",
                parts[1].strip().capitalize() if parts[1] else sentence,
                f"Simplified: {sentence[:50]}..."
            ]
        elif " when " in sentence:
            parts = sentence.split(" when ", 1)
            return [
                f"When {parts[1].strip()}, {parts[0].strip().lower()}.",
                parts[0].strip() + ".",
                f"Consider: {sentence[:40]}..."
            ]
        else:
            return [
                sentence[:len(sentence)//2].strip() + ".",
                sentence[len(sentence)//2:].strip().capitalize(),
                f"Break this into shorter sentences: {sentence}"
            ]

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
