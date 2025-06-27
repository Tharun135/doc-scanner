"""
Enhanced AI suggestion system for better writing recommendations.
This module provides improved prompt engineering and context-aware suggestions.
"""

import json
import re
import ollama
import logging
from typing import Dict, List, Optional, Any
from .prompt_templates import (
    AdvancedPromptTemplates, 
    classify_feedback_type, 
    get_document_type_from_string,
    DocumentType,
    FeedbackType
)

logger = logging.getLogger(__name__)

class EnhancedAISuggestionEngine:
    """
    Enhanced AI suggestion engine with better prompt engineering,
    context awareness, and domain-specific knowledge.
    """
    
    def __init__(self, model_name: str = "mistral-7b-instruct"):
        self.model_name = model_name
        self.style_guide_context = self._load_style_guide_context()
        
    def _load_style_guide_context(self) -> str:
        """Load relevant style guide information for context."""
        return """
Style Guide Context:
- Use active voice instead of passive voice
- Keep sentences under 25 words for better readability
- Use specific, concrete terms instead of vague language
- Avoid jargon unless necessary for technical audiences
- Use parallel structure in lists and series
- Prefer shorter, simpler words when possible
- Use inclusive language and avoid bias
- Be consistent with terminology throughout documents
        """
    
    def create_enhanced_prompt(self, feedback_text: str, sentence_context: str = "", 
                             document_type: str = "general", writing_goals: List[str] = None) -> str:
        """
        Create a comprehensive, context-aware prompt for better AI suggestions.
        
        Args:
            feedback_text: The specific feedback or issue identified
            sentence_context: The actual sentence or text context
            document_type: Type of document (technical, marketing, academic, etc.)
            writing_goals: Specific writing goals or requirements
        """
        
        writing_goals = writing_goals or ["clarity", "conciseness", "professionalism"]
        goals_text = ", ".join(writing_goals)
        
        prompt = f"""You are an expert writing coach and editor specializing in {document_type} writing. Your goal is to provide specific, actionable suggestions that improve {goals_text}.

{self.style_guide_context}

CONTEXT:
Document Type: {document_type}
Writing Goals: {goals_text}
Sentence/Text: "{sentence_context}"
Issue Identified: {feedback_text}

TASK:
Provide a specific, actionable suggestion to improve this text. Your response should include:

1. SPECIFIC PROBLEM: What exactly is wrong (be precise)
2. SUGGESTED IMPROVEMENT: Exact text changes or rewriting
3. EXPLANATION: Why this change improves the writing
4. ALTERNATIVE OPTIONS: 1-2 alternative approaches if applicable

EXAMPLES OF GOOD SUGGESTIONS:

Issue: "Passive voice detected"
Text: "The report was completed by the team."
Response:
- PROBLEM: Uses passive voice, making the sentence less direct and engaging
- IMPROVEMENT: "The team completed the report."
- EXPLANATION: Active voice is more direct, clearer, and engaging for readers
- ALTERNATIVE: "The team finished the report" (for variety)

Issue: "Sentence too long and complex"
Text: "The system, which was developed by our engineering team over the course of several months, provides users with the ability to manage their data more effectively."
Response:
- PROBLEM: 25+ words with embedded clauses make it hard to follow
- IMPROVEMENT: "Our engineering team developed the system over several months. It helps users manage their data more effectively."
- EXPLANATION: Breaking into two sentences improves readability and flow
- ALTERNATIVE: "The new system helps users manage data more effectively. Our engineering team spent several months developing it."

Now provide your suggestion for the current issue:"""

        return prompt
    
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None) -> Dict[str, Any]:
        """
        Generate an enhanced AI suggestion with advanced prompt engineering.
        
        Returns:
            Dict containing suggestion, confidence, and metadata
        """
        try:
            # Convert string to enum
            doc_type_enum = get_document_type_from_string(document_type)
            feedback_type_enum = classify_feedback_type(feedback_text)
            
            # Build advanced prompt
            prompt_data = AdvancedPromptTemplates.build_complete_prompt(
                feedback_type=feedback_type_enum,
                issue_description=feedback_text,
                sentence_context=sentence_context,
                document_type=doc_type_enum,
                writing_goals=writing_goals
            )
            
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': prompt_data["system"]
                    },
                    {
                        'role': 'user',
                        'content': prompt_data["user"]
                    }
                ],
                options={
                    'temperature': 0.2,  # Even lower for more consistent responses
                    'top_p': 0.85,
                    'max_tokens': 400,
                    'repeat_penalty': 1.1
                }
            )
            
            suggestion = response['message']['content'].strip()
            
            return {
                "suggestion": suggestion,
                "confidence": "high",
                "method": "advanced_ai_prompt",
                "feedback_type": feedback_type_enum.value,
                "context_used": {
                    "document_type": document_type,
                    "writing_goals": writing_goals,
                    "feedback_classification": feedback_type_enum.value,
                    "has_sentence_context": bool(sentence_context),
                    "prompt_template": "advanced"
                }
            }
            
        except Exception as e:
            logger.error(f"Advanced AI suggestion failed: {str(e)}")
            # Fall back to improved rule-based suggestions
            return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)
    
    def generate_smart_fallback_suggestion(self, feedback_text: str, 
                                         sentence_context: str = "") -> Dict[str, Any]:
        """
        Generate intelligent rule-based suggestions when AI is unavailable.
        Much more sophisticated than the original fallback.
        """
        feedback_lower = feedback_text.lower()
        context_lower = sentence_context.lower()
        
        # Advanced pattern matching with context awareness
        suggestions = {
            # Passive voice patterns
            ("passive", "voice"): {
                "suggestion": self._generate_active_voice_suggestion(sentence_context),
                "confidence": "medium"
            },
            
            # Sentence length and complexity
            ("long", "sentence"): {
                "suggestion": self._generate_sentence_shortening_suggestion(sentence_context),
                "confidence": "medium"
            },
            
            # Word choice improvements
            ("vague", "unclear"): {
                "suggestion": "Replace vague terms with specific, concrete language. Add precise details, numbers, or examples to clarify your meaning.",
                "confidence": "medium"
            },
            
            # Readability improvements
            ("complex", "difficult"): {
                "suggestion": "Simplify complex language: use shorter words, break up long phrases, and explain technical terms. Consider your audience's expertise level.",
                "confidence": "medium"
            },
            
            # Structure and flow
            ("transition", "flow", "choppy"): {
                "suggestion": "Improve flow with transition words: 'However' (contrast), 'Therefore' (conclusion), 'Furthermore' (addition), 'Meanwhile' (time), 'In contrast' (comparison).",
                "confidence": "high"
            }
        }
        
        # Find best matching suggestion
        for patterns, suggestion_data in suggestions.items():
            if any(pattern in feedback_lower for pattern in patterns):
                return {
                    "suggestion": suggestion_data["suggestion"],
                    "confidence": suggestion_data["confidence"],
                    "method": "smart_fallback",
                    "pattern_matched": patterns
                }
        
        # Default enhanced suggestion
        return {
            "suggestion": self._generate_general_improvement_suggestion(feedback_text, sentence_context),
            "confidence": "low",
            "method": "general_fallback"
        }
    
    def _generate_active_voice_suggestion(self, sentence: str) -> str:
        """Generate specific active voice suggestions."""
        if not sentence:
            return "Convert passive voice to active voice: identify who performs the action and make them the subject."
        
        # Look for common passive patterns
        passive_patterns = [
            (r'was (\w+ed|en)\s+by', r'The subject should \1'),
            (r'were (\w+ed|en)\s+by', r'The subjects should \1'),
            (r'is (\w+ed|en)\s+by', r'The subject \1s'),
            (r'are (\w+ed|en)\s+by', r'The subjects \1')
        ]
        
        for pattern, suggestion in passive_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return f"Convert to active voice. Example structure: {suggestion}. Make the actor the subject of the sentence."
        
        return "Rewrite in active voice: move the action performer to the beginning and make them the subject."
    
    def _generate_sentence_shortening_suggestion(self, sentence: str) -> str:
        """Generate specific suggestions for shortening sentences."""
        if not sentence:
            return "Break long sentences into shorter ones. Aim for 15-20 words per sentence."
        
        word_count = len(sentence.split())
        suggestions = []
        
        if word_count > 30:
            suggestions.append("This sentence is very long (30+ words). Break it into 2-3 shorter sentences.")
        elif word_count > 20:
            suggestions.append("Consider breaking this into two sentences for better readability.")
        
        # Look for specific patterns that can be simplified
        if ' which ' in sentence.lower() or ' that ' in sentence.lower():
            suggestions.append("Consider removing relative clauses ('which'/'that') and making separate sentences.")
        
        if sentence.count(',') > 2:
            suggestions.append("This sentence has multiple clauses. Consider breaking at commas to create separate sentences.")
        
        if ' and ' in sentence.lower() and sentence.count(' and ') > 1:
            suggestions.append("Multiple 'and' conjunctions suggest this could be broken into separate sentences.")
        
        return " ".join(suggestions) if suggestions else "Break this long sentence into shorter, more digestible parts."
    
    def _generate_general_improvement_suggestion(self, feedback: str, context: str) -> str:
        """Generate a thoughtful general suggestion based on available information."""
        suggestions = [
            "Consider these improvements:",
            "• Use specific, concrete language instead of vague terms",
            "• Ensure each sentence has one main idea",
            "• Use active voice when possible",
            "• Add examples or details to support your points"
        ]
        
        if "technical" in feedback.lower() or "jargon" in feedback.lower():
            suggestions.append("• Define technical terms for your audience")
        
        if "formal" in feedback.lower():
            suggestions.append("• Adjust formality level to match your audience and purpose")
        
        return "\n".join(suggestions)

# Global instance for easy use
ai_engine = EnhancedAISuggestionEngine()

def get_enhanced_ai_suggestion(feedback_text: str, sentence_context: str = "",
                             document_type: str = "general", 
                             writing_goals: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get enhanced AI suggestions.
    
    Args:
        feedback_text: The feedback or issue identified
        sentence_context: The actual sentence or text
        document_type: Type of document (technical, marketing, academic, etc.)
        writing_goals: List of writing goals (clarity, conciseness, etc.)
    
    Returns:
        Dictionary with suggestion and metadata
    """
    return ai_engine.generate_contextual_suggestion(
        feedback_text, sentence_context, document_type, writing_goals
    )
