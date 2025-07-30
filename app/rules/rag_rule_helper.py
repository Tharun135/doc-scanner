"""
RAG Rule Helper - Integrates RAG with rule-based detection
This module provides a unified interface for rules to use RAG with smart fallback.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup
import html

# Import RAG system
try:
    from ..rag_system import get_rag_suggestion
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logging.warning("RAG system not available - using fallback only")

logger = logging.getLogger(__name__)

def check_with_rag(content: str, rule_patterns: Dict[str, Any], 
                   rule_name: str = "unknown", 
                   fallback_suggestions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Universal RAG-enabled rule checker with smart fallback.
    
    Args:
        content: The text content to check
        rule_patterns: Dictionary containing pattern detection logic
        rule_name: Name of the rule for logging/debugging
        fallback_suggestions: List of fallback suggestions when RAG is unavailable
    
    Returns:
        List of suggestion dictionaries with RAG enhancements
    """
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Execute rule pattern detection (this varies by rule)
    detected_issues = []
    if 'detect_function' in rule_patterns:
        detected_issues = rule_patterns['detect_function'](content, text_content)
    
    # Process each detected issue with RAG
    for issue in detected_issues:
        if not isinstance(issue, dict):
            # Convert string issues to dict format
            issue = {
                "text": issue if isinstance(issue, str) else str(issue),
                "start": 0,
                "end": len(issue if isinstance(issue, str) else str(issue)),
                "message": issue if isinstance(issue, str) else str(issue),
                "context": text_content[:200]  # First 200 chars as context
            }
        
        # Try RAG first
        rag_suggestion = None
        if RAG_AVAILABLE:
            try:
                feedback_text = issue.get("message", "")
                sentence_context = issue.get("context", "")
                
                rag_result = get_rag_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context,
                    document_type="technical",
                    document_content=text_content[:1000]  # First 1000 chars for context
                )
                
                if rag_result and rag_result.get("suggestion"):
                    rag_suggestion = rag_result["suggestion"]
                    logger.info(f"RAG suggestion generated for {rule_name}")
                else:
                    logger.debug(f"RAG returned no suggestion for {rule_name}")
                    
            except Exception as e:
                logger.error(f"RAG error in {rule_name}: {e}")
        
        # Use RAG suggestion if available, otherwise use fallback
        if rag_suggestion:
            suggestions.append({
                "text": issue.get("text", ""),
                "start": issue.get("start", 0),
                "end": issue.get("end", 0),
                "message": rag_suggestion,
                "method": "rag_enhanced",
                "rule": rule_name,
                "original_issue": issue.get("message", "")
            })
        else:
            # Smart fallback
            fallback_message = issue.get("message", "")
            if fallback_suggestions:
                # Use rule-specific fallback
                fallback_message = fallback_suggestions[0] if fallback_suggestions else fallback_message
            
            suggestions.append({
                "text": issue.get("text", ""),
                "start": issue.get("start", 0),
                "end": issue.get("end", 0),
                "message": fallback_message,
                "method": "rule_based_fallback",
                "rule": rule_name,
                "note": "RAG unavailable - using rule-based suggestion"
            })
    
    return suggestions

def detect_passive_voice_issues(content: str, text_content: str) -> List[Dict[str, Any]]:
    """
    Detect passive voice constructions in text.
    Returns list of detected issues with context.
    """
    import re
    import spacy
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_content)
        sentences = list(doc.sents)
    except:
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text_content)
        sentences = [s.strip() for s in sentences if s.strip()]
    
    for sent in sentences:
        if hasattr(sent, 'text'):
            sent_text = sent.text.strip()
            # spaCy-based passive detection
            spacy_passive = any(token.dep_ == "auxpass" for token in sent)
        else:
            sent_text = str(sent).strip()
            spacy_passive = False
        
        # Pattern-based passive voice detection
        passive_patterns = [
            r'\bis\s+\w+ed\b',  # "is needed", "is required"
            r'\bare\s+\w+ed\b',  # "are needed", "are required"
            r'\bwas\s+\w+ed\b', # "was created", "was developed"
            r'\bwere\s+\w+ed\b', # "were created", "were developed"
            r'\bhas\s+been\s+\w+ed\b', # "has been created"
            r'\bhave\s+been\s+\w+ed\b', # "have been created"
            r'\bbeing\s+\w+ed\b', # "being processed"
            r'\bto\s+be\s+\w+ed\b', # "to be processed"
        ]
        
        pattern_passive = any(re.search(pattern, sent_text, re.IGNORECASE) for pattern in passive_patterns)
        
        if spacy_passive or pattern_passive:
            # Find passive phrase for specific feedback
            passive_phrase = ""
            for pattern in passive_patterns:
                match = re.search(pattern, sent_text, re.IGNORECASE)
                if match:
                    passive_phrase = match.group()
                    break
            
            issue_text = passive_phrase if passive_phrase else "passive voice construction"
            
            issues.append({
                "text": issue_text,
                "start": 0,  # Could be improved with actual position
                "end": len(issue_text),
                "message": f"Passive voice detected: '{issue_text}' - convert to active voice for clearer, more direct communication.",
                "context": sent_text,
                "sentence": sent_text
            })
    
    return issues

def detect_long_sentence_issues(content: str, text_content: str) -> List[Dict[str, Any]]:
    """
    Detect long sentences that may need splitting.
    """
    import re
    import spacy
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_content)
        sentences = list(doc.sents)
    except:
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text_content)
        sentences = [s.strip() for s in sentences if s.strip()]
    
    for sent in sentences:
        if hasattr(sent, 'text'):
            sent_text = sent.text.strip()
        else:
            sent_text = str(sent).strip()
        
        # Count words
        word_count = len(sent_text.split())
        
        if word_count > 25:  # Threshold for long sentences
            issues.append({
                "text": sent_text[:50] + "..." if len(sent_text) > 50 else sent_text,
                "start": 0,
                "end": len(sent_text),
                "message": f"Long sentence detected ({word_count} words). Consider breaking into shorter sentences for better readability.",
                "context": sent_text,
                "sentence": sent_text,
                "word_count": word_count
            })
    
    return issues

def detect_modal_verb_issues(content: str, text_content: str) -> List[Dict[str, Any]]:
    """
    Detect modal verb issues (can/may/could usage).
    """
    import re
    import spacy
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_content)
        sentences = list(doc.sents)
    except:
        # Fallback: treat as single text
        doc = None
        sentences = [text_content]
    
    # Check "may" usage
    may_pattern = r'\bmay\b'
    matches = re.finditer(may_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Find sentence containing this match
        target_sentence = ""
        if doc:
            match_pos = match.start()
            for sent in doc.sents:
                if sent.start_char <= match_pos <= sent.end_char:
                    target_sentence = sent.text.strip()
                    break
        else:
            target_sentence = text_content
        
        if target_sentence:
            issues.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "message": f"Modal verb 'may' usage. Context needed to determine if 'may' (possibility) or 'can' (permission) is more appropriate.",
                "context": target_sentence,
                "sentence": target_sentence
            })
    
    # Check "could" usage
    could_pattern = r'\bcould\b'
    matches = re.finditer(could_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        target_sentence = ""
        if doc:
            match_pos = match.start()
            for sent in doc.sents:
                if sent.start_char <= match_pos <= sent.end_char:
                    target_sentence = sent.text.strip()
                    break
        else:
            target_sentence = text_content
        
        if target_sentence:
            issues.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "message": f"Use of 'could' detected. Ensure 'could' is used for past actions or polite requests, not as a substitute for 'can'.",
                "context": target_sentence,
                "sentence": target_sentence
            })
    
    return issues
