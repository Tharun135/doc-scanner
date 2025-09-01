"""
Enhanced AI suggestion system with integrated document rewriting capabilities
Extends the existing ai_suggestion endpoint with rewriting features
"""

import logging
from typing import Dict, Optional, Any
from .rewriter.ollama_rewriter import get_rewriter

logger = logging.getLogger(__name__)

class EnhancedSuggestionSystem:
    """Enhanced suggestion system that integrates rule-based feedback with AI rewriting."""
    
    def __init__(self):
        self.rewriter = get_rewriter()
    
    def enhance_suggestion_with_rewriting(self, original_result: Dict, 
                                       feedback_text: str, 
                                       sentence_context: str,
                                       enhancement_mode: str = "auto") -> Dict:
        """
        Enhance an existing AI suggestion result with rewriting capabilities.
        
        Args:
            original_result: The original AI suggestion result
            feedback_text: The feedback/issue description
            sentence_context: The original sentence
            enhancement_mode: "auto", "clarity", "simplicity", or "balanced"
        
        Returns:
            Enhanced result dictionary with rewriting suggestions
        """
        try:
            # Determine the best rewriting mode based on feedback
            if enhancement_mode == "auto":
                rewriting_mode = self._determine_rewriting_mode(feedback_text)
            else:
                rewriting_mode = enhancement_mode
            
            # Get AI rewriting suggestion
            rewrite_result = self.rewriter.rewrite_sentence(sentence_context, rewriting_mode)
            
            if rewrite_result.get("success"):
                # Enhance the original result with rewriting
                enhanced_result = original_result.copy()
                
                # Add rewriting to suggestion if original suggestion is weak or missing
                original_suggestion = original_result.get("suggestion", "").strip()
                rewritten_text = rewrite_result.get("rewritten", "").strip()
                
                # Use rewritten version if it's significantly different and better
                if (rewritten_text and 
                    rewritten_text != sentence_context and 
                    (not original_suggestion or len(original_suggestion) < 10)):
                    
                    enhanced_result["suggestion"] = rewritten_text
                    enhanced_result["rewrite_confidence"] = "high"
                    
                    # Enhance AI answer with rewriting insights
                    readability_info = self._format_readability_improvement(
                        rewrite_result.get("scores", {})
                    )
                    
                    original_ai_answer = original_result.get("ai_answer", "")
                    enhanced_result["ai_answer"] = f"{original_ai_answer}\n\n**AI Rewrite Suggestion:** {rewritten_text}\n{readability_info}"
                
                # Add rewriting metadata
                enhanced_result["rewriting"] = {
                    "available": True,
                    "mode_used": rewriting_mode,
                    "alternative_suggestion": rewritten_text,
                    "readability_scores": rewrite_result.get("scores", {}),
                    "method": "ollama_rewriter"
                }
                
                # Update method to indicate enhancement
                original_method = enhanced_result.get("method", "unknown")
                enhanced_result["method"] = f"{original_method}+rewriter"
                
                logger.info(f"Enhanced suggestion with rewriting (mode: {rewriting_mode})")
                return enhanced_result
            
            else:
                # Rewriting failed, return original result with note
                logger.warning(f"Rewriting failed: {rewrite_result.get('error', 'Unknown error')}")
                original_result["rewriting"] = {
                    "available": False,
                    "error": rewrite_result.get("error", "Rewriting service unavailable")
                }
                return original_result
                
        except Exception as e:
            logger.error(f"Error enhancing suggestion with rewriting: {e}")
            # Return original result if enhancement fails
            original_result["rewriting"] = {
                "available": False,
                "error": str(e)
            }
            return original_result
    
    def _determine_rewriting_mode(self, feedback_text: str) -> str:
        """Determine the best rewriting mode based on the feedback text."""
        feedback_lower = feedback_text.lower()
        
        # Map feedback types to rewriting modes
        if any(term in feedback_lower for term in ['complex', 'difficult', 'hard to read', 'unclear']):
            return "simplicity"
        elif any(term in feedback_lower for term in ['ambiguous', 'confusing', 'vague']):
            return "clarity"
        elif any(term in feedback_lower for term in ['passive voice', 'wordy', 'verbose']):
            return "clarity"
        else:
            return "balanced"
    
    def _format_readability_improvement(self, scores: Dict) -> str:
        """Format readability improvement information for display."""
        original_scores = scores.get("original", {})
        rewritten_scores = scores.get("rewritten", {})
        
        if not original_scores or not rewritten_scores:
            return ""
        
        original_ease = original_scores.get("flesch_reading_ease", 0)
        rewritten_ease = rewritten_scores.get("flesch_reading_ease", 0)
        improvement = rewritten_ease - original_ease
        
        if improvement > 5:
            return f"📈 **Readability improved** by {improvement:.1f} points (easier to read)"
        elif improvement < -5:
            return f"📉 **Note:** Readability decreased by {abs(improvement):.1f} points"
        else:
            return "📊 **Readability:** Similar level maintained"

def get_full_document_rewrite_suggestion(content: str, mode: str = "balanced") -> Dict:
    """
    Get a complete document rewrite suggestion (for potential future UI integration).
    
    Args:
        content: Full document content to rewrite
        mode: Rewriting mode
    
    Returns:
        Complete rewrite result with metadata
    """
    try:
        rewriter = get_rewriter()
        result = rewriter.rewrite_document(content, mode)
        
        # Format for API response
        if result.get("success"):
            return {
                "success": True,
                "original_content": content,
                "rewritten_content": result.get("rewritten_text", ""),
                "improvements": result.get("improvements", {}),
                "readability_scores": result.get("scores", {}),
                "metadata": result.get("metadata", {}),
                "mode": mode,
                "suggestion_type": "full_document_rewrite"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "original_content": content,
                "rewritten_content": content  # Return original on failure
            }
    
    except Exception as e:
        logger.error(f"Error in full document rewrite: {e}")
        return {
            "success": False,
            "error": str(e),
            "original_content": content,
            "rewritten_content": content
        }

def get_readability_analysis(text: str) -> Dict:
    """Get readability analysis for any text."""
    try:
        rewriter = get_rewriter()
        scores = rewriter.calculate_readability(text)
        
        return {
            "success": True,
            "text_length": len(text),
            "word_count": len(text.split()),
            "scores": scores,
            "recommendations": _get_readability_recommendations(scores)
        }
    
    except Exception as e:
        logger.error(f"Error in readability analysis: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def _get_readability_recommendations(scores: Dict) -> list:
    """Generate recommendations based on readability scores."""
    recommendations = []
    
    flesch_ease = scores.get("flesch_reading_ease", 50)
    flesch_grade = scores.get("flesch_kincaid_grade", 10)
    
    if flesch_ease < 30:
        recommendations.append("Consider simplifying complex sentences")
    if flesch_ease < 50:
        recommendations.append("Try using shorter sentences and simpler words")
    if flesch_grade > 12:
        recommendations.append("Content may be too complex for general audience")
    if flesch_grade > 16:
        recommendations.append("Consider breaking down technical concepts")
    
    if not recommendations:
        recommendations.append("Readability is within acceptable range")
    
    return recommendations

# Global instance
_enhanced_suggestion_system = None

def get_enhanced_suggestion_system() -> EnhancedSuggestionSystem:
    """Get the global enhanced suggestion system instance."""
    global _enhanced_suggestion_system
    if _enhanced_suggestion_system is None:
        _enhanced_suggestion_system = EnhancedSuggestionSystem()
    return _enhanced_suggestion_system
