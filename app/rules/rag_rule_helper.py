"""
RAG Rule Helper - Integrates RAG with rule-based detection
This module provides a unified interface for rules to use RAG with smart fallback.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup
import html
import re

# EMERGENCY TOGGLE: Set to False to disable RAG for performance
RAG_ENABLED = True  # Enabled for AI-only functionality

# Local AI system is the only source - No more fallbacks needed!
try:
    from .smart_rag_manager import get_smart_rag_suggestion, get_rag_status
    SMART_RAG_AVAILABLE = True
    get_smart_rag_suggestion = get_smart_rag_suggestion  # Ensure it's properly bound
    logging.info("Smart local AI manager loaded successfully - fallbacks disabled")
except ImportError as e:
    SMART_RAG_AVAILABLE = False
    get_smart_rag_suggestion = None  # Set to None if not available
    logging.error(f"Smart local AI manager not available: {e}")

# REMOVED: Legacy optimizers and fallback systems - AI only now
FAST_RAG_AVAILABLE = False
RAG_AVAILABLE = False  # Disable old systems

logger = logging.getLogger(__name__)

def format_rag_suggestion(raw_suggestion: str, rule_name: str = "unknown") -> str:
    """
    Format RAG suggestion to be user-friendly and crisp.
    Converts "OPTION 1: ..., OPTION 2: ..., WHY: ..." to clean suggestion.
    """
    if not raw_suggestion:
        return ""
    
    try:
        # Extract the first option as the primary suggestion
        option_match = re.search(r'OPTION\s+1:\s*([^\n]+)', raw_suggestion, re.IGNORECASE)
        if option_match:
            primary_suggestion = option_match.group(1).strip()
            
            # Create a crisp, clear message based on the rule type
            if rule_name == "passive_voice":
                return f"Convert to active voice: '{primary_suggestion}'"
            elif rule_name == "long_sentences":
                return f"Consider breaking into shorter sentences: '{primary_suggestion}'"
            elif rule_name == "modal_verbs":
                return f"Use more precise language: '{primary_suggestion}'"
            else:
                return f"Consider rewriting as: '{primary_suggestion}'"
        
        # If no OPTION format found, extract the first sentence
        sentences = raw_suggestion.split('\n')
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.startswith(('OPTION', 'WHY:')):
                if rule_name == "passive_voice":
                    return f"Convert to active voice: '{sentence}'"
                else:
                    return f"Consider rewriting as: '{sentence}'"
        
        # Fallback: return first non-empty line
        for line in sentences:
            line = line.strip()
            if line:
                return line
                
    except Exception as e:
        logger.error(f"Error formatting RAG suggestion: {e}")
    
    # Final fallback
    return "Consider revising this sentence for clarity."

def check_with_rag(content: str, rule_name: str = "unknown", 
                   description: str = "", rule_patterns=None, **kwargs) -> List[str]:
    """
    AI-only checker using unlimited local Ollama AI.
    No fallbacks - AI-powered suggestions only.
    
    Args:
        content: The text content to check
        rule_name: Name of the rule for logging/debugging
        description: Description of what the rule checks for
        rule_patterns: Optional rule patterns (ignored - AI handles everything)
        **kwargs: Additional arguments (ignored)
    
    Returns:
        List of AI-generated suggestion strings
    """
    # Early return if RAG is disabled
    if not RAG_ENABLED:
        return []
    
    suggestions = []
    
    try:
        # Use local AI system exclusively - no fallbacks
        if SMART_RAG_AVAILABLE and get_smart_rag_suggestion is not None:
            # Get AI suggestion using unlimited local Ollama
            rag_suggestion, source = get_smart_rag_suggestion(
                text=content,
                rule_name=rule_name,
                context=description
            )
            
            if rag_suggestion:
                formatted_suggestion = format_rag_suggestion(rag_suggestion, rule_name)
                if formatted_suggestion:
                    suggestions.append(formatted_suggestion)
                    logger.info(f"AI suggestion provided for {rule_name} from {source}")
                else:
                    logger.warning(f"AI suggestion formatting failed for {rule_name}")
            else:
                logger.warning(f"AI returned no suggestion for {rule_name}")
        else:
            logger.error(f"Local AI system not available for {rule_name} - no fallbacks enabled")
            
    except Exception as e:
        logger.error(f"Local AI error for {rule_name}: {e}")
    
    return suggestions

def check_with_rag_advanced(content: str, rule_patterns: Dict[str, Any], 
                   rule_name: str = "unknown", 
                   fallback_suggestions: List[str] = None) -> List[Dict[str, Any]]:
    """
    AI-only rule checker with unlimited local Ollama.
    Returns None if AI fails - no smart fallbacks.
    
    Args:
        content: The text content to check
        rule_patterns: Dictionary containing pattern detection logic
        rule_name: Name of the rule for logging/debugging
        fallback_suggestions: Ignored - no fallbacks used
    
    Returns:
        List of AI-generated suggestion dictionaries, or None if AI failed
    """
    # Early return if RAG is disabled
    if not RAG_ENABLED:
        return []
    
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Execute rule pattern detection (this varies by rule)
    detected_issues = []
    if 'detect_function' in rule_patterns:
        detected_issues = rule_patterns['detect_function'](content, text_content)
    
    # If no issues detected by the pattern, return empty list (not None)
    if not detected_issues:
        return []
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
        
        # Use local AI exclusively - no fallbacks
        if SMART_RAG_AVAILABLE and get_smart_rag_suggestion is not None:
            try:
                feedback_text = issue.get("message", "")
                sentence_context = issue.get("context", "")
                
                # Use unlimited local AI
                local_ai_result, source = get_smart_rag_suggestion(
                    text=sentence_context or feedback_text,
                    rule_name=rule_name,
                    context=feedback_text
                )
                
                if local_ai_result:
                    # Format the AI suggestion to be user-friendly
                    formatted_suggestion = format_rag_suggestion(local_ai_result, rule_name)
                    
                    suggestions.append({
                        "text": issue.get("text", ""),
                        "start": issue.get("start", 0),
                        "end": issue.get("end", 0),
                        "message": formatted_suggestion,
                        "method": "ai_unlimited",
                        "rule": rule_name,
                        "source": source,
                        "original_issue": issue.get("message", "")
                    })
                    logger.info(f"AI suggestion generated for {rule_name} from {source}")
                else:
                    logger.warning(f"AI returned no suggestion for {rule_name}")
                    # Return None to indicate AI failure - let rule use fallback
                    return None
                    
            except Exception as e:
                logger.error(f"Local AI error in {rule_name}: {e}")
                # Return None to indicate AI failure - let rule use fallback
                return None
        else:
            logger.error(f"Local AI system not available for {rule_name}")
            # Return None to indicate AI failure - let rule use fallback
            return None
    
    return suggestions

def detect_passive_voice_issues(content: str, text_content: str) -> List[Dict[str, Any]]:
    """
    Detect passive voice constructions in text.
    Returns list of detected issues with context.
    """
    import re
    from .spacy_utils import get_nlp_model
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = get_nlp_model()
        doc = nlp(text_content)
        sentences = list(doc.sents)
    except:
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text_content)
        sentences = [s.strip() for s in sentences if s.strip()]
    
    current_pos = 0  # Track position in the full text
    
    for sent in sentences:
        if hasattr(sent, 'text'):
            sent_text = sent.text.strip()
            # For spaCy sentences, use the actual character positions
            sent_start = sent.start_char
            sent_end = sent.end_char
            # spaCy-based passive detection
            spacy_passive = any(token.dep_ == "auxpass" for token in sent)
        else:
            sent_text = str(sent).strip()
            # For regex fallback, find the position in the full text
            sent_start = text_content.find(sent_text, current_pos)
            if sent_start == -1:
                sent_start = current_pos  # Fallback if not found
            sent_end = sent_start + len(sent_text)
            current_pos = sent_end
            spacy_passive = False
        
        # Pattern-based passive voice detection
        # Regular past participles (ending in -ed)
        regular_passive_patterns = [
            r'\bis\s+\w+ed\b',  # "is needed", "is required"
            r'\bare\s+\w+ed\b',  # "are needed", "are required"
            r'\bwas\s+\w+ed\b', # "was created", "was developed"
            r'\bwere\s+\w+ed\b', # "were created", "were developed"
            r'\bhas\s+been\s+\w+ed\b', # "has been created"
            r'\bhave\s+been\s+\w+ed\b', # "have been created"
            r'\bbeing\s+\w+ed\b', # "being processed"
            r'\bto\s+be\s+\w+ed\b', # "to be processed"
        ]
        
        # Irregular past participles (common ones)
        irregular_participles = [
            'written', 'taken', 'given', 'shown', 'known', 'thrown', 'drawn', 'driven',
            'flown', 'grown', 'blown', 'broken', 'chosen', 'frozen', 'spoken', 'stolen',
            'woken', 'forgotten', 'hidden', 'ridden', 'risen', 'fallen', 'eaten', 'beaten',
            'seen', 'done', 'gone', 'come', 'become', 'overcome', 'run', 'begun', 'sung',
            'rung', 'swung', 'hung', 'spun', 'won', 'built', 'bent', 'sent', 'spent',
            'lent', 'meant', 'kept', 'left', 'felt', 'dealt', 'dreamt', 'learnt', 'burnt',
            'thought', 'brought', 'caught', 'taught', 'fought', 'bought', 'sought', 'sold',
            'told', 'held', 'found', 'bound', 'wound', 'lost', 'cost', 'cut', 'put', 'set',
            'hit', 'let', 'bet', 'shut', 'hurt', 'split', 'quit', 'spread'
        ]
        
        # Create patterns for irregular participles
        irregular_passive_patterns = []
        for participle in irregular_participles:
            irregular_passive_patterns.extend([
                fr'\bis\s+{participle}\b',  # "is written"
                fr'\bare\s+{participle}\b',  # "are written"  
                fr'\bwas\s+{participle}\b', # "was written"
                fr'\bwere\s+{participle}\b', # "were written"
                fr'\bhas\s+been\s+{participle}\b', # "has been written"
                fr'\bhave\s+been\s+{participle}\b', # "have been written"
                fr'\bbeing\s+{participle}\b', # "being written"
                fr'\bto\s+be\s+{participle}\b', # "to be written"
            ])
        
        all_passive_patterns = regular_passive_patterns + irregular_passive_patterns
        pattern_passive = any(re.search(pattern, sent_text, re.IGNORECASE) for pattern in all_passive_patterns)
        
        if spacy_passive or pattern_passive:
            # SAFETY CHECK: Skip very short sentences that are unlikely to be meaningful passive voice
            if len(sent_text.strip()) < 8:  # Skip very short fragments like "The", "It is", etc.
                continue
                
            # Find passive phrase for specific feedback
            passive_phrase = ""
            phrase_start = sent_start  # Default to sentence start
            phrase_end = sent_end      # Default to sentence end
            
            for pattern in all_passive_patterns:
                match = re.search(pattern, sent_text, re.IGNORECASE)
                if match:
                    passive_phrase = match.group()
                    # Calculate the position of the passive phrase within the full text
                    phrase_start = sent_start + match.start()
                    phrase_end = sent_start + match.end()
                    break
            
            issue_text = passive_phrase if passive_phrase else "passive voice construction"
            
            issues.append({
                "text": issue_text,
                "start": phrase_start,  # FIXED: Use actual position
                "end": phrase_end,      # FIXED: Use actual end position
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
    from .spacy_utils import get_nlp_model
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = get_nlp_model()
        doc = nlp(text_content)
        sentences = list(doc.sents)
    except:
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text_content)
        sentences = [s.strip() for s in sentences if s.strip()]
    
    current_pos = 0  # Track position in the full text
    
    for sent in sentences:
        if hasattr(sent, 'text'):
            sent_text = sent.text.strip()
            # For spaCy sentences, use the actual character positions
            sent_start = sent.start_char
            sent_end = sent.end_char
        else:
            sent_text = str(sent).strip()
            # For regex fallback, find the position in the full text
            sent_start = text_content.find(sent_text, current_pos)
            if sent_start == -1:
                sent_start = current_pos  # Fallback if not found
            sent_end = sent_start + len(sent_text)
            current_pos = sent_end
        
        # Count words
        word_count = len(sent_text.split())
        
        if word_count > 25:  # Threshold for long sentences
            issues.append({
                "text": sent_text[:50] + "..." if len(sent_text) > 50 else sent_text,
                "start": sent_start,  # FIXED: Use actual position in text
                "end": sent_end,      # FIXED: Use actual end position
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
    from .spacy_utils import get_nlp_model
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = get_nlp_model()
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
