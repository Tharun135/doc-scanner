"""
Emergency Fast Response System
Provides immediate suggestions when AI is slow or failing.
Used only when AI takes too long or returns poor results.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_emergency_suggestion(feedback_text: str, sentence_context: str) -> Dict[str, Any]:
    """
    Provide immediate pattern-based suggestions when AI fails or is too slow.
    This is NOT a fallback - it's an emergency speed system.
    """
    feedback_lower = feedback_text.lower()
    
    if "passive voice" in feedback_lower and sentence_context:
        # Fast passive voice conversion
        suggestion = _convert_passive_to_active_fast(sentence_context)
        return {
            "suggestion": suggestion,
            "ai_answer": f"Fast conversion for: {feedback_text}",
            "confidence": "medium",
            "method": "emergency_fast",
            "note": "Fast pattern-based conversion (AI was slow)"
        }
    
    elif "long sentence" in feedback_lower and sentence_context:
        # Fast sentence splitting
        suggestion = _split_sentence_fast(sentence_context)
        return {
            "suggestion": suggestion,
            "ai_answer": f"Fast splitting for: {feedback_text}",
            "confidence": "medium", 
            "method": "emergency_fast",
            "note": "Fast sentence splitting (AI was slow)"
        }
    
    else:
        # Generic fast improvement
        return {
            "suggestion": f"OPTION 1: Review and improve based on: {feedback_text}\nOPTION 2: Address the writing issue identified\nOPTION 3: Revise for better clarity\nWHY: Fast response for {feedback_text}",
            "ai_answer": f"Generic improvement for: {feedback_text}",
            "confidence": "low",
            "method": "emergency_fast",
            "note": "Generic fast response (AI was slow)"
        }

def _convert_passive_to_active_fast(sentence: str) -> str:
    """Fast pattern-based passive to active conversion."""
    
    # Handle "was written by" pattern
    if "was written by" in sentence.lower():
        match = re.search(r'(.+?)\s+was\s+written\s+by\s+(.+)', sentence, re.IGNORECASE)
        if match:
            document = match.group(1).strip()
            author = match.group(2).strip().rstrip('.')
            return f"""OPTION 1: {author} wrote {document.lower()}
OPTION 2: {author} authored {document.lower()}
OPTION 3: {author} created {document.lower()}
WHY: Converts passive voice to active voice for clarity."""
    
    # Handle "was created by" pattern
    elif "was created by" in sentence.lower():
        match = re.search(r'(.+?)\s+was\s+created\s+by\s+(.+)', sentence, re.IGNORECASE)
        if match:
            item = match.group(1).strip()
            creator = match.group(2).strip().rstrip('.')
            return f"""OPTION 1: {creator} created {item.lower()}
OPTION 2: {creator} developed {item.lower()}
OPTION 3: {creator} built {item.lower()}
WHY: Converts passive voice to active voice for clarity."""
    
    # Handle "are displayed" pattern
    elif "are displayed" in sentence.lower():
        item = sentence.replace(" are displayed", "").replace("The ", "").strip()
        return f"""OPTION 1: The system displays {item.lower()}
OPTION 2: The interface shows {item.lower()}  
OPTION 3: You can view {item.lower()}
WHY: Converts passive voice to active voice for clarity."""
    
    # Handle "is processed" pattern
    elif "is processed" in sentence.lower():
        match = re.search(r'(.+?)\s+is\s+processed\s+by\s+(.+)', sentence, re.IGNORECASE)
        if match:
            item = match.group(1).strip()
            processor = match.group(2).strip().rstrip('.')
            return f"""OPTION 1: {processor} processes {item.lower()}
OPTION 2: {processor} handles {item.lower()}
OPTION 3: {processor} manages {item.lower()}
WHY: Converts passive voice to active voice for clarity."""
    
    # Generic conversion
    else:
        # Try to identify subject and convert
        if " was " in sentence:
            parts = sentence.split(" was ", 1)
            if len(parts) == 2:
                subject = parts[0].strip()
                rest = parts[1].strip().rstrip('.')
                return f"""OPTION 1: The system {rest} {subject.lower()}
OPTION 2: Someone {rest} {subject.lower()}
OPTION 3: {subject} gets {rest}
WHY: Converts passive voice to active voice for clarity."""
        
        return f"""OPTION 1: Convert this to active voice: {sentence}
OPTION 2: Rewrite to show who performs the action
OPTION 3: Make the subject clear and active
WHY: Converts passive voice to active voice for clarity."""

def _split_sentence_fast(sentence: str) -> str:
    """Fast sentence splitting."""
    
    # Split on "and" if sentence is long
    if " and " in sentence and len(sentence) > 50:
        parts = sentence.split(" and ", 1)
        sentence1 = parts[0].strip().rstrip('.') + '.'
        sentence2 = parts[1].strip()
        if not sentence2.endswith('.'):
            sentence2 += '.'
        
        return f"""OPTION 1 has sentence 1: {sentence1.rstrip('.')}, sentence 2: {sentence2.rstrip('.')}
OPTION 2 has sentence 1: {sentence1.rstrip('.')}, sentence 2: Additionally, {sentence2.lower().rstrip('.')}
OPTION 3: {sentence1} {sentence2}
WHY: Breaks long sentence into clearer segments."""
    
    # Split on "which" 
    elif " which " in sentence:
        parts = sentence.split(" which ", 1)
        sentence1 = parts[0].strip().rstrip('.') + '.'
        sentence2 = "This " + parts[1].strip()
        if not sentence2.endswith('.'):
            sentence2 += '.'
        
        return f"""OPTION 1 has sentence 1: {sentence1.rstrip('.')}, sentence 2: {sentence2.rstrip('.')}
OPTION 2 has sentence 1: {sentence1.rstrip('.')}, sentence 2: It {parts[1].strip().rstrip('.')}
OPTION 3: {sentence1} {sentence2}
WHY: Breaks long sentence into clearer segments."""
    
    # Generic splitting
    else:
        words = sentence.split()
        if len(words) > 15:
            mid = len(words) // 2
            sentence1 = " ".join(words[:mid]).rstrip('.') + '.'
            sentence2 = " ".join(words[mid:])
            if not sentence2.endswith('.'):
                sentence2 += '.'
                
            return f"""OPTION 1 has sentence 1: {sentence1.rstrip('.')}, sentence 2: {sentence2.rstrip('.')}
OPTION 2: Break this into shorter sentences
OPTION 3: Consider revising for clarity
WHY: Breaks long sentence into clearer segments."""
        
        return f"""OPTION 1: This sentence could be shorter
OPTION 2: Consider breaking into parts
OPTION 3: Revise for better clarity
WHY: Addresses sentence length for readability."""
