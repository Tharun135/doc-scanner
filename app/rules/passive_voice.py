import re
import spacy
from bs4 import BeautifulSoup
import html

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Import anaphora resolution for context-aware suggestions
try:
    from .anaphora_resolution import resolve_pronoun_subject, should_convert_to_active
    ANAPHORA_AVAILABLE = True
except ImportError:
    ANAPHORA_AVAILABLE = False
    import logging
    logging.debug(f"Anaphora resolution not available for {__name__}")

# Use shared spaCy instance to avoid conflicts
try:
    from app.app import nlp
except ImportError:
    # Fallback if we can't import the shared instance
    try:
        nlp = spacy.load("en_core_web_sm")
        # Increase max_length to handle large documents
        nlp.max_length = 3000000
    except OSError:
        # If spaCy model not available, create a minimal instance
        import warnings
        warnings.warn("spaCy model not available, passive voice detection will be limited")
        nlp = None

def is_code_or_diagram(text: str) -> bool:
    """Detect code blocks, diagrams, and technical syntax that shouldn't be analyzed."""
    text = text.strip().lower()
    if not text:
        return True
    
    # Code/diagram markers
    code_markers = ['mermaid', 'flowchart', 'sequencediagram', 'graph', 'json', 'yaml', 'xml', 'html', '```', '{', '[', '<', '-->', '|', '---', ':::', '~~~']
    if any(text.startswith(marker) for marker in code_markers):
        return True
    
    # High syntax density (>20% special chars = likely code)
    syntax_chars = sum(1 for c in text if c in '{}[]()<>|→-=:')
    if len(text) > 10 and syntax_chars / len(text) > 0.2:
        return True
    
    return False

def check(content, previous_sentence=None, next_sentence=None):
    """
    Check for passive voice in content.
    
    Args:
        content: The sentence content to check
        previous_sentence: Optional previous sentence for context resolution
        next_sentence: Optional next sentence for context
    
    Returns:
        List of suggestions (strings or dicts with context info)
    """
    suggestions = []
    
    # Skip if no spaCy available
    if nlp is None:
        return suggestions
    
    # Strip HTML tags
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # Detect passive voice: look for "auxpass" dependencies
    # Pre-process content to remove admonition lines entirely
    lines = text_content.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip lines that are markdown admonitions
        if re.match(r'^\s*!!!\s+\w+(?:\s+"[^"]*")?\s*.*$', line, re.IGNORECASE):
            continue
        filtered_lines.append(line)
    
    # Re-process the filtered content with spaCy
    filtered_content = '\n'.join(filtered_lines)
    if not filtered_content.strip():
        return suggestions
        
    filtered_doc = nlp(filtered_content)
    
    for token in filtered_doc:
        sentence_text = token.sent.text.strip()
        
        # Skip if token is in a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sentence_text, content):
            continue
        
        # Skip code blocks and diagrams
        if is_code_or_diagram(sentence_text):
            continue
            
        is_passive = False
        target_verb = ""
        
        if token.dep_ == "auxpass":
            is_passive = True
            target_verb = token.head.lemma_.lower()
        elif getattr(token, 'dep_', '') == "":
            # Regex fallback when using DummySpacy
            regular_passive = [
                r'\bis\s+\w+ed\b', r'\bare\s+\w+ed\b', r'\bwas\s+\w+ed\b', r'\bwere\s+\w+ed\b',
                r'\bhas\s+been\s+\w+ed\b', r'\bhave\s+been\s+\w+ed\b', r'\bbeing\s+\w+ed\b', r'\bto\s+be\s+\w+ed\b'
            ]
            irregular_participles = [
                'written', 'taken', 'given', 'shown', 'known', 'thrown', 'drawn', 'driven',
                'flown', 'grown', 'blown', 'broken', 'chosen', 'frozen', 'spoken', 'stolen',
                'woken', 'forgotten', 'hidden', 'ridden', 'risen', 'fallen', 'eaten', 'beaten',
                'seen', 'done', 'gone', 'come', 'become', 'overcome', 'run', 'begun', 'sung',
                'rung', 'swung', 'hung', 'spun', 'won', 'built', 'bent', 'sent', 'spent',
                'lent', 'meant', 'kept', 'left', 'felt', 'dealt', 'dreamt', 'learnt', 'burnt',
                'thought', 'brought', 'caught', 'taught', 'fought', 'bought', 'sought', 'sold',
                'told', 'held', 'found', 'bound', 'wound', 'lost', 'cost', 'cut', 'put', 'set',
                'hit', 'let', 'bet', 'shut', 'hurt', 'split', 'quit', 'spread', 'made', 'read', 'kept'
            ]
            all_patterns = regular_passive + [fr'\b(is|are|was|were|has been|have been|being|to be)\s+{p}\b' for p in irregular_participles]
            
            for pattern in all_patterns:
                if re.search(pattern, sentence_text, re.IGNORECASE):
                    is_passive = True
                    target_verb = "regex_match"
                    break
            
            # Since dummy tokens will iterate for every word in the sentence, only process the sentence once
            # to avoid duplicate suggestions for the same sentence
            if is_passive and any(s.get('text') == sentence_text for s in suggestions if isinstance(s, dict)):
                continue

        if is_passive:
            # PRECISISON FIX: Whitelist technical state verbs that are appropriate in passive/state form
            if target_verb in ['abstract', 'integrate', 'store', 'equip', 'locate', 'configure', 'setup', 'set']:
                continue
            # ============================================================
            # CONTEXT ANALYSIS: Determine if passive should be converted
            # ============================================================
            
            # Check for explicit actor (e.g., "by the system")
            has_explicit_actor = " by " in sentence_text.lower()
            
            # Try to resolve subject if anaphora resolution is available
            resolved_info = None
            conversion_note = ""
            should_convert_flag = True
            preservation_reason = None
            
            if ANAPHORA_AVAILABLE and previous_sentence:
                # Attempt to resolve pronouns from previous sentence
                resolved = resolve_pronoun_subject(sentence_text, previous_sentence)
                
                # Check if conversion is beneficial
                should_convert_flag, reason = should_convert_to_active(sentence_text, resolved)
                
                if not should_convert_flag:
                    # Passive voice is actually clearer here
                    preservation_reason = reason
                elif resolved and resolved.get('confidence') in ['high', 'medium']:
                    # We have context - provide specific guidance
                    resolved_info = {
                        'resolved_subject': resolved['subject'],
                        'explanation': resolved['explanation'],
                        'conversion_note': f" The subject '{resolved['subject']}' from the previous sentence can be used."
                    }
                    conversion_note = resolved_info['conversion_note']
            
            # ============================================================
            # DECISION LOGIC: Classify based on context
            # ============================================================
            
            if not should_convert_flag:
                # DECISION: no_change - Passive voice is intentional/clearer
                suggestion = {
                    'text': sentence_text,
                    'start': 0,
                    'end': len(sentence_text),
                    'message': 'Passive voice detected',
                    'decision_type': 'no_change',
                    'rule': 'passive_voice',
                    'reviewer_rationale': preservation_reason or 'Passive voice appropriate in this context - actor is unknown, irrelevant, or intentionally omitted for focus on the action itself.'
                }
            elif has_explicit_actor:
                # DECISION: rewrite - Actor is known, active voice clearer
                suggestion = {
                    'text': sentence_text,
                    'start': 0,
                    'end': len(sentence_text),
                    'message': 'Passive voice with known actor detected',
                    'decision_type': 'rewrite',
                    'rule': 'passive_voice',
                    'reviewer_rationale': 'Actor is explicitly stated - active voice provides clearer, more direct communication and improves readability.',
                    'ai_suggestion': None  # Will be filled by enrichment service
                }
            elif resolved_info:
                # DECISION: rewrite - Actor can be inferred from context
                suggestion = {
                    'text': sentence_text,
                    'start': 0,
                    'end': len(sentence_text),
                    'message': 'Passive voice detected - actor can be inferred from context',
                    'decision_type': 'rewrite',
                    'rule': 'passive_voice',
                    'reviewer_rationale': f'Actor can be inferred from context.{conversion_note} Active voice improves clarity.',
                    'ai_suggestion': None  # Will be filled by enrichment service
                }
            else:
                # DECISION: no_change - Actor unknown/intentionally omitted
                suggestion = {
                    'text': sentence_text,
                    'start': 0,
                    'end': len(sentence_text),
                    'message': 'Passive voice detected',
                    'decision_type': 'no_change',
                    'rule': 'passive_voice',
                    'reviewer_rationale': 'Actor intentionally omitted - passive voice is appropriate for system state descriptions, security restrictions, or when the actor is unknown or irrelevant to the reader.'
                }
            
            # Avoid duplicate suggestions for the same sentence
            if not any(s.get('text') == sentence_text for s in suggestions if isinstance(s, dict)):
                suggestions.append(suggestion)
    
    return suggestions
