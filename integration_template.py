"""
Integration Point: Connect decision logger to DocScanner app.

This shows EXACTLY how to wire the rewrite decision logger into your existing code.

Add this to app.py or wherever you process sentences.
"""

from app.rewrite_decision_logger import (
    get_history_logger, 
    capture_rewrite_suggestion,
    capture_user_response,
    ConfidenceLevel
)
import time


def analyze_sentence_with_logging(sentence: str, rules: list, document_context: dict) -> dict:
    """
    REPLACE your existing analyze_sentence() with this version.
    
    This is the CRITICAL integration point.
    """
    # Get logger
    history_logger = get_history_logger()
    
    # Track timing
    start_time = time.time()
    
    # Run existing analysis
    feedback_items = []
    for rule in rules:
        try:
            feedback = rule(sentence)
            if feedback:
                feedback_items.extend(feedback if isinstance(feedback, list) else [feedback])
        except Exception as e:
            continue
    
    # For EACH feedback item, log the decision
    for feedback_text in feedback_items:
        # Determine which rule triggered
        rule_id, rule_name = _identify_rule_from_feedback(feedback_text)
        
        # Calculate confidence
        confidence = _calculate_confidence(sentence, rule_id, feedback_text)
        
        # Generate suggested rewrite (if applicable)
        suggested_rewrite = _generate_suggested_rewrite(sentence, rule_id)
        
        # Determine if rewrite should be suggested
        should_suggest_rewrite = suggested_rewrite is not None
        
        # Create justification
        justification = _create_justification(rule_name, feedback_text)
        
        # Log the decision
        decision = capture_rewrite_suggestion(
            sentence=sentence,
            rule_id=rule_id,
            rule_name=rule_name,
            suggested_rewrite=suggested_rewrite or "",
            justification=justification,
            confidence=confidence,
            document_context={
                "doc_id": document_context.get("doc_id", "unknown"),
                "doc_type": document_context.get("doc_type", "manual"),
                "sentence_before": document_context.get("sentence_before", ""),
                "sentence_after": document_context.get("sentence_after", ""),
                "paragraph": document_context.get("paragraph", ""),
                "severity": document_context.get("severity", "medium"),
                "metadata": document_context.get("metadata", {})
            }
        )
        
        history_logger.log_decision(decision)
        
        # Store decision ID for later user response tracking
        feedback_text = f"{feedback_text}|||DECISION_ID:{decision.id}"
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    return {
        "sentence": sentence,
        "feedback": feedback_items,
        "analysis_time_ms": elapsed_ms
    }


def log_user_response(decision_id: str, accepted: bool, 
                     actual_rewrite: str = None, 
                     rejection_reason: str = None,
                     time_to_decision_ms: int = None):
    """
    Call this when user accepts/rejects a suggestion.
    
    Integration points:
    - User clicks "Accept" → accepted=True
    - User clicks "Reject" → accepted=False
    - User edits manually → capture actual_rewrite
    - User provides reason → capture rejection_reason
    """
    capture_user_response(
        decision_id=decision_id,
        accepted=accepted,
        actual_rewrite=actual_rewrite,
        rejection_reason=rejection_reason,
        time_to_decision_ms=time_to_decision_ms
    )


# Helper functions (adapt to your codebase)

def _identify_rule_from_feedback(feedback_text: str) -> tuple[str, str]:
    """
    Identify which rule triggered from feedback text.
    
    CUSTOMIZE THIS based on your actual feedback format.
    """
    feedback_lower = feedback_text.lower()
    
    # Map feedback patterns to rules
    rule_patterns = {
        "passive voice": ("PASSIVE_VOICE", "Passive Voice"),
        "long sentence": ("LONG_SENTENCES", "Long Sentences"),
        "adverb": ("ADVERBS", "Weak Adverbs"),
        "very": ("VERY", "Overuse of 'Very'"),
        "nominalization": ("NOMINALIZATIONS", "Nominalizations"),
        "vague": ("VAGUE_TERMS", "Vague Terms"),
        "tense": ("VERB_TENSE", "Verb Tense Consistency"),
        "grammar": ("GRAMMAR_BASIC", "Basic Grammar"),
        "consistency": ("CONSISTENCY", "Terminology Consistency"),
        "readability": ("READABILITY", "Readability")
    }
    
    for pattern, (rule_id, rule_name) in rule_patterns.items():
        if pattern in feedback_lower:
            return rule_id, rule_name
    
    return "UNKNOWN", "Unknown Rule"


def _calculate_confidence(sentence: str, rule_id: str, feedback: str) -> str:
    """
    Calculate confidence level for the suggestion.
    
    CUSTOMIZE THIS based on your actual heuristics.
    """
    # Simple heuristics (replace with your actual logic)
    
    # High confidence cases
    if rule_id == "PASSIVE_VOICE" and "by" in sentence.lower():
        return ConfidenceLevel.HIGH.value
    
    if rule_id == "LONG_SENTENCES" and len(sentence.split()) > 35:
        return ConfidenceLevel.HIGH.value
    
    if rule_id == "VERY" and sentence.count("very") > 1:
        return ConfidenceLevel.HIGH.value
    
    # Low confidence cases
    if rule_id in ["READABILITY", "CONSISTENCY"]:
        return ConfidenceLevel.MEDIUM.value
    
    # Uncertain cases
    if "consider" in feedback.lower() or "may" in feedback.lower():
        return ConfidenceLevel.LOW.value
    
    # Default
    return ConfidenceLevel.MEDIUM.value


def _generate_suggested_rewrite(sentence: str, rule_id: str) -> str:
    """
    Generate a suggested rewrite (if possible).
    
    INTEGRATE WITH YOUR AI REWRITE SYSTEM.
    For now, return None to indicate "no automatic rewrite available".
    """
    # TODO: Integrate with your AI improvement system
    # from app.ai_improvement import generate_rewrite
    # return generate_rewrite(sentence, rule_id)
    
    return None  # Return None if no rewrite generated


def _create_justification(rule_name: str, feedback_text: str) -> str:
    """
    Create a clear justification for the suggestion.
    
    CUSTOMIZE based on your rules.
    """
    # Use the feedback text as base, but make it more specific
    if "passive voice" in feedback_text.lower():
        return "Passive voice obscures the actor and makes writing less direct. Active voice clarifies who performs the action."
    
    if "long sentence" in feedback_text.lower():
        return "Long sentences reduce readability and comprehension. Breaking them into shorter sentences improves clarity."
    
    if "adverb" in feedback_text.lower():
        return "Adverbs often weaken writing. Choosing stronger, more specific verbs eliminates the need for adverbs."
    
    # Default: use the feedback as-is
    return feedback_text


# Example integration in your main app

def example_integration_in_app_py():
    """
    Show how to integrate in your main app.py
    
    REPLACE your existing review_document() function with this pattern.
    """
    
    def review_document_with_logging(content: str, rules: list):
        """Enhanced version that logs decisions."""
        
        # Get sentences (your existing logic)
        sentences = split_into_sentences(content)
        
        all_feedback = []
        
        for i, sentence in enumerate(sentences):
            # Build context
            context = {
                "doc_id": "current_document",
                "doc_type": "manual",  # Detect from content
                "sentence_before": sentences[i-1] if i > 0 else "",
                "sentence_after": sentences[i+1] if i < len(sentences)-1 else "",
                "paragraph": get_paragraph_containing(sentence, content),
                "severity": "medium"
            }
            
            # Analyze WITH logging
            result = analyze_sentence_with_logging(sentence, rules, context)
            
            if result["feedback"]:
                all_feedback.append({
                    "sentence": sentence,
                    "issues": result["feedback"]
                })
        
        return all_feedback


def split_into_sentences(content: str) -> list:
    """Your existing sentence splitting logic."""
    # TODO: Use your actual implementation
    return content.split('. ')


def get_paragraph_containing(sentence: str, content: str) -> str:
    """Get the paragraph containing this sentence."""
    # TODO: Implement based on your document structure
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if sentence in para:
            return para
    return sentence


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║  Rewrite Decision Logger - Integration Guide            ║
    ║                                                          ║
    ║  Step 1: Replace analyze_sentence() with                ║
    ║          analyze_sentence_with_logging()                ║
    ║                                                          ║
    ║  Step 2: Wire up user response callbacks                ║
    ║          (Accept/Reject buttons)                         ║
    ║                                                          ║
    ║  Step 3: Run app normally - decisions auto-logged       ║
    ║                                                          ║
    ║  Step 4: Mine logged decisions:                         ║
    ║          python mine_real_history.py                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Test example
    test_sentence = "The document was reviewed by the team."
    test_rules = []  # Your actual rules
    test_context = {
        "doc_id": "test",
        "doc_type": "manual",
        "sentence_before": "This is context.",
        "sentence_after": "Next sentence.",
        "paragraph": "This is context. The document was reviewed by the team. Next sentence."
    }
    
    # This would log to data/rewrite_history.jsonl
    # result = analyze_sentence_with_logging(test_sentence, test_rules, test_context)
    print("✅ Integration template ready")
    print("📝 Edit your app.py to use analyze_sentence_with_logging()")
