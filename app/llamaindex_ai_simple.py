"""
Simple Direct Ollama AI for Doc Scanner - No RAG, No Fallbacks
Fast and reliable AI suggestions using direct Ollama API calls.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SimpleLlamaIndexAISuggestionEngine:
    """
    Simplified AI engine using direct Ollama API calls.
    Fast, reliable, no complex RAG or fallback systems.
    """
    
    def __init__(self, model_name: str = "tinyllama"):
        self.model_name = model_name
        self.is_initialized = False
        
        # Test if Ollama is working
        if self._test_ollama_service():
            self.is_initialized = True
            logger.info(f"Direct Ollama AI initialized with {model_name}")
        else:
            logger.error("Ollama service not available")
    
    def _test_ollama_service(self) -> bool:
        """Test if Ollama service is available and responsive."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None,
                                     document_content: str = "") -> Dict[str, Any]:
        """
        Generate AI suggestion using direct Ollama API.
        Fast and simple - no complex RAG system.
        """
        if not self.is_initialized:
            return {
                "suggestion": "AI service not available. Please start Ollama service.",
                "ai_answer": "Service unavailable",
                "confidence": "low",
                "method": "ai_error",
                "error": "Ollama not running"
            }
        
        try:
            start_time = time.time()
            
            # Create focused prompt
            prompt = self._create_prompt(feedback_text, sentence_context)
            
            # Direct Ollama API call with timeout
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=8  # 8 second timeout for speed
            )
            
            elapsed = time.time() - start_time
            
            # If AI is too slow (over 5 seconds), use emergency system next time
            if elapsed > 5:
                logger.warning(f"AI took {elapsed:.1f}s - consider using emergency suggestions")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                if ai_response and len(ai_response) > 20:  # Ensure meaningful response
                    # Format response consistently
                    formatted = self._format_response(ai_response, feedback_text, sentence_context)
                    
                    logger.info(f"AI suggestion generated in {elapsed:.2f}s")
                    return {
                        "suggestion": formatted,
                        "ai_answer": ai_response,
                        "confidence": "high",
                        "method": "direct_ollama",
                        "model": self.model_name,
                        "processing_time": elapsed
                    }
                else:
                    logger.warning("AI returned empty/short response, using emergency system")
                    # Use emergency system for immediate response
                    from .emergency_suggestions import get_emergency_suggestion
                    return get_emergency_suggestion(feedback_text, sentence_context)
            
            # If we get here, AI failed - use emergency system
            logger.error(f"Ollama API failed: {response.status_code if response else 'No response'}")
            from .emergency_suggestions import get_emergency_suggestion
            return get_emergency_suggestion(feedback_text, sentence_context)
            
        except requests.Timeout:
            logger.warning("AI timeout - using emergency system")
            from .emergency_suggestions import get_emergency_suggestion 
            return get_emergency_suggestion(feedback_text, sentence_context)
        except Exception as e:
            logger.error(f"AI error: {e} - using emergency system")
            from .emergency_suggestions import get_emergency_suggestion
            return get_emergency_suggestion(feedback_text, sentence_context)
    
    def _create_prompt(self, feedback_text: str, sentence_context: str) -> str:
        """Create a focused prompt for the specific writing issue."""
        if "passive voice" in feedback_text.lower():
            return f'''Convert this passive voice sentence to active voice: "{sentence_context}"

Be concise. Format:
OPTION 1: [active voice version]
OPTION 2: [alternative active voice]
OPTION 3: [third active voice version]
WHY: Converts passive to active voice.

Do not add extra words or explanations.'''

        elif "long sentence" in feedback_text.lower() or "sentence too long" in feedback_text.lower():
            return f'''Break this long sentence into 2 shorter sentences:

"{sentence_context}"

Provide exactly 3 options in this format:
OPTION 1 has sentence 1: [first part], sentence 2: [second part]
OPTION 2 has sentence 1: [alternative first part], sentence 2: [alternative second part]
OPTION 3: [combined alternative approach]
WHY: Breaks long sentence into clearer segments.

Be direct and concise.'''

        elif "modal verb" in feedback_text.lower():
            return f'''Remove modal verbs to make this more direct:

"{sentence_context}"

Provide exactly 3 options in this format:
OPTION 1: [direct version without modal verbs]
OPTION 2: [alternative direct version]
OPTION 3: [third direct alternative]
WHY: Removes unnecessary modal verbs for direct communication.

Be direct and concise.'''

        else:
            return f'''Improve this text to address: {feedback_text}

"{sentence_context}"

Provide exactly 3 options in this format:
OPTION 1: [improved version]
OPTION 2: [alternative improvement]
OPTION 3: [third alternative]
WHY: [brief explanation]

Be direct and concise.'''
    
    def _format_response(self, ai_response: str, feedback_text: str, sentence_context: str) -> str:
        """Ensure AI response has consistent format."""
        # If AI already formatted correctly, use it
        if "OPTION 1:" in ai_response and "WHY:" in ai_response:
            return ai_response.strip()
        
        # If not formatted, create proper format
        lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
        
        if len(lines) >= 3:
            # Use first 3 lines as options
            formatted = f"""OPTION 1: {lines[0]}
OPTION 2: {lines[1]}
OPTION 3: {lines[2]}
WHY: Addresses {feedback_text.lower()} for better writing."""
            return formatted
        elif len(lines) >= 1:
            # Single response - create variations
            base = lines[0]
            formatted = f"""OPTION 1: {base}
OPTION 2: Alternative: {base}
OPTION 3: Consider: {base}
WHY: Addresses {feedback_text.lower()} for better writing."""
            return formatted
        else:
            # Fallback if AI gave no useful response
            return f"""OPTION 1: Review and improve this text based on: {feedback_text}
OPTION 2: Address the writing issue: {feedback_text}
OPTION 3: Consider revising for better clarity
WHY: Addresses {feedback_text.lower()} for better writing."""

# Create global instance
def get_ai_suggestion(feedback_text: str, sentence_context: str = "", **kwargs) -> Dict[str, Any]:
    """Convenience function for getting AI suggestions."""
    global _ai_engine
    if '_ai_engine' not in globals():
        _ai_engine = SimpleLlamaIndexAISuggestionEngine()
    
    return _ai_engine.generate_contextual_suggestion(feedback_text, sentence_context, **kwargs)

# Compatibility with existing code
LlamaIndexAISuggestionEngine = SimpleLlamaIndexAISuggestionEngine
