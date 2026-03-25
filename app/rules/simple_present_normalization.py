"""
Simple Present Tense Normalization Rule

This module detects sentences that should be converted to simple present tense
according to documentation style guide standards.

This is NOT grammar correction - it is documentation normalization.

Key invariants:
1. Tense conversion is allowed only when it preserves time, obligation, and intent
2. Compliance + conditions block all automatic tense changes
3. Historical text is never rewritten
4. AI executes only after eligibility is proven
5. Silence is better than a wrong rewrite
"""

import logging

logger = logging.getLogger(__name__)

# Try to import spacy but handle gracefully if not available
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except ImportError:
    logger.warning("spaCy not available for tense detection - feature will be limited")
    SPACY_AVAILABLE = False
    nlp = None
except Exception as e:
    logger.warning(f"Could not load spaCy model: {e}")
    SPACY_AVAILABLE = False
    nlp = None

# Verb tense markers
PAST_TENSE_TAGS = {"VBD", "VBN"}
FUTURE_MARKERS = {"will", "shall", "going"}
PRESENT_TAGS = {"VBP", "VBZ"}


def is_non_sentential(text: str) -> bool:
    """
    Detect non-sentential text (titles, headings, fragments, code blocks).
    
    These should NOT be analyzed by sentence-level rules.
    
    Returns True if text is:
    - A heading or title
    - A gerund phrase used as a label
    - A fragment without a verb
    - A short noun phrase
    - Code blocks (mermaid, json, yaml, etc.)
    - Technical syntax/markup
    """
    text = text.strip()
    
    if not text:
        return True
    
    # Bullet list items are labels, not sentences
    # Common patterns: "- Item", "* Item", "1. Item", "• Item"
    # Or no marker but no terminal punctuation and short
    if not text.endswith(('.', '!', '?')):
        # Likely a bullet/list item if it's a noun phrase without a verb
        # or has participles used as adjectives
        words = text.split()
        if len(words) <= 12:  # Typical bullet items are short
            # Check for bullet markers at the start (after parsing)
            if any(text.startswith(marker) for marker in ['-', '*', '•', '+']):
                return True
            # Or numbered lists
            if len(words) > 0 and words[0].rstrip('.').isdigit():
                return True
    
    # Parenthetical descriptions are typically labels, not sentences
    # "(integrated in...)", "Service (description)", etc.
    if text.count('(') >= 1 and text.count(')') >= 1:
        # If most of the text is in parentheses, or there's no verb outside them
        paren_start = text.find('(')
        paren_end = text.rfind(')')
        if paren_start < paren_end:
            before_parens = text[:paren_start].strip()
            # Title + parenthetical description pattern
            if len(before_parens.split()) <= 5:  # Short title before parens
                return True
    
    # Code block markers
    code_markers = [
        'mermaid', 'flowchart', 'sequenceDiagram', 'graph',  # Mermaid
        'json', 'yaml', 'xml', 'html', 'css', 'javascript',  # Code
        '```', '{', '[', '<',  # Syntax
        '-->', '|', '---', ':::', '~~~'  # Diagram syntax
    ]
    
    # Check if text starts with code/diagram syntax
    text_lower = text.lower()
    if any(text_lower.startswith(marker) for marker in code_markers):
        return True
    
    # Check for high density of technical syntax (likely code/diagram)
    syntax_chars = sum(1 for c in text if c in '{}[]()<>|→-=:')
    if len(text) > 10 and syntax_chars / len(text) > 0.2:
        return True
    
    # Short fragments are often titles
    if len(text.split()) <= 3:
        return True
    
    if not SPACY_AVAILABLE or not nlp:
        # Fallback: basic heuristics without spaCy
        # Gerund phrases used as titles typically start with -ing
        if text.split()[0].endswith('ing'):
            return True
        # No sentence-ending punctuation often indicates a title
        if not text.rstrip().endswith(('.', '!', '?', ':')):
            return True
        return False
    
    doc = nlp(text)
    
    # Check if there's any finite verb (excludes participles used as adjectives)
    # VBG = gerund/present participle, VBN = past participle
    # When VBN appears without auxiliary (e.g., "integrated in"), it's likely an adjective
    has_finite_verb = False
    for tok in doc:
        if tok.pos_ in {"VERB", "AUX"}:
            # Exclude non-finite forms: gerunds and past participles without auxiliaries
            if tok.tag_ in {"VBG", "VBN"}:
                # Check if VBN has an auxiliary (e.g., "was integrated" = finite)
                has_aux = any(child.dep_ == "aux" for child in tok.children) or any(tok.dep_ == "aux" for tok in doc)
                if not has_aux:
                    continue  # VBN without aux = adjective, not finite verb
            has_finite_verb = True
            break
    
    if not has_finite_verb:
        # No finite verb = likely a title or gerund phrase
        return True
    
    # Gerund phrase used as title (starts with -ing word)
    if text[0].isupper() and any(tok.tag_ == "VBG" and tok.i == 0 for tok in doc):
        return True
    
    # Very short noun phrase (likely a label)
    if len(text.split()) <= 5:
        pos_tags = [tok.pos_ for tok in doc]
        if all(pos in {"NOUN", "PROPN", "ADJ", "DET", "ADP"} for pos in pos_tags):
            return True
    
    return False


def is_metadiscourse(sentence: str) -> bool:
    """
    Detect metadiscourse or structural sentences that introduce content.
    
    Metadiscourse sentences:
    - Introduce examples, figures, tables, code blocks
    - Guide readers structurally through the document
    - Are intentionally neutral and should never be rewritten
    
    Examples:
    - "Here's an example of a properly configured certificate:"
    - "The following figure shows the architecture:"
    - "Below is a sample configuration:"
    - "This section describes the installation process."
    
    Returns True if sentence is metadiscourse.
    """
    s = sentence.lower().strip()
    
    # Check for common metadiscourse patterns
    metadiscourse_patterns = [
        # Example introducers
        "here is",
        "here's",
        "here are",
        "below is",
        "below are",
        "shown below",
        "following is",
        "the following",
        "above is",
        "shown above",
        
        # Figure/table/code references
        "figure shows",
        "table shows",
        "example shows",
        "diagram shows",
        "screenshot shows",
        "code shows",
        
        # Section/content introducers
        "this section",
        "this chapter",
        "this document",
        "this guide",
        "this tutorial",
        
        # Structural phrases
        "example of",
        "sample of",
        "illustration of",
    ]
    
    # Check if sentence starts with metadiscourse
    for pattern in metadiscourse_patterns:
        if s.startswith(pattern):
            return True
    
    # Check if sentence contains metadiscourse phrases
    for pattern in ["example of", "sample of", "illustration of"]:
        if pattern in s:
            return True
    
    # Check if sentence ends with colon (common for introducers)
    if s.endswith(":"):
        # Additional check: must also contain metadiscourse keywords
        metadiscourse_keywords = [
            "example", "sample", "following", "below", "above",
            "figure", "table", "diagram", "screenshot", "code",
            "section", "chapter"
        ]
        if any(keyword in s for keyword in metadiscourse_keywords):
            return True
    
    return False


def detect_verb_tense(sentence: str) -> str:
    """
    Detects the main verb tense of a sentence.
    
    Returns: 'past', 'present', 'future', 'mixed', or 'unknown'
    """
    if not SPACY_AVAILABLE or not nlp:
        # Fallback: basic string matching
        s_lower = sentence.lower()
        if any(marker in s_lower for marker in [" will ", " shall ", "going to"]):
            return "future"
        if any(past in s_lower for past in [" was ", " were ", " had ", " did "]):
            return "past"
        return "unknown"
    
    doc = nlp(sentence)
    
    has_past = False
    has_present = False
    has_future = False
    
    for token in doc:
        if token.pos_ == "AUX" or token.pos_ == "VERB":
            if token.tag_ in PAST_TENSE_TAGS:
                has_past = True
            elif token.tag_ in PRESENT_TAGS:
                has_present = True
            elif token.lower_ in FUTURE_MARKERS:
                has_future = True
    
    if has_future:
        return "future"
    if has_past and has_present:
        return "mixed"
    if has_past:
        return "past"
    if has_present:
        return "present"
    
    return "unknown"


def classify_sentence_for_tense(sentence: str) -> str:
    """
    Classify a sentence to determine if tense conversion is appropriate.
    
    Returns one of:
    - 'instructional': Procedures, steps (always eligible)
    - 'descriptive': System behavior (always eligible)
    - 'explanatory': Examples (eligible with restructuring)
    - 'historical': Past events (never eligible)
    - 'compliance_conditional': Requirements with conditions (never eligible)
    """
    s = sentence.lower()
    
    # Historical / temporal (never rewrite)
    if any(x in s for x in [
        "in version", "previously", "earlier", "historically",
        "was introduced", "was added", "was removed", "was deprecated",
        "used to", "at that time", "in the past"
    ]):
        return "historical"
    
    # Conditional clauses with past tense describe prerequisites (historical context)
    # "when X was configured", "after Y was installed", etc.
    if any(x in s for x in [" when ", " after "]) and any(x in s for x in [" was ", " were "]):
        return "historical"
    
    # Compliance + conditions (never auto rewrite)
    if (
        any(x in s for x in [" must ", " shall ", " required "]) and
        any(x in s for x in [" if ", " after ", " before ", " unless ", " in case ", " when "])
    ):
        return "compliance_conditional"
    
    # Explanatory examples (eligible)
    if s.startswith(("for example", "for instance", "in this setup", "in this case", "typically")):
        return "explanatory"
    
    # Instructional
    if any(s.startswith(x) for x in [
        "click", "configure", "set", "select", "enter", "verify",
        "run", "execute", "install", "open", "close", "save",
        "create", "delete", "modify", "update", "enable", "disable"
    ]):
        return "instructional"
    
    # Default: descriptive system behavior
    return "descriptive"


def can_convert_to_simple_present(sentence: str) -> tuple[bool, str]:
    """
    Determine if a sentence can be safely converted to simple present tense.
    
    Returns:
        (allowed: bool, reason: str)
        
    Reasons:
        - 'already_present': Sentence is already in present tense
        - 'historical': Describes past events
        - 'compliance_conditional': Requirement with conditions
        - 'instructional': Safe to convert
        - 'descriptive': Safe to convert
        - 'explanatory': Safe to convert
    """
    tense = detect_verb_tense(sentence)
    classification = classify_sentence_for_tense(sentence)
    
    # Already in present tense
    if tense == "present":
        return False, "already_present"
    
    # Never rewrite these classes
    if classification in {"historical", "compliance_conditional"}:
        return False, classification
    
    # Eligible classes
    return True, classification


def build_simple_present_prompt(sentence: str) -> str:
    """
    Build AI prompt for tense conversion.
    
    This prompt is intentionally narrow and forbids creativity.
    """
    return f"""Rewrite the following sentence in simple present tense.

Rules (MANDATORY):
- Preserve the original meaning exactly.
- Do NOT add or remove conditions.
- Do NOT change obligation strength (must, shall, required).
- Do NOT remove technical terms or qualifiers.
- Do NOT introduce new actions.
- Do NOT explain your answer.
- Output only the rewritten sentence.

Sentence:
"{sentence}"
""".strip()


def validate_simple_present_rewrite(original: str, rewritten: str) -> tuple[bool, str]:
    """
    Validate that an AI-generated rewrite is safe and appropriate.
    
    This validator is deliberately strict to prevent semantic drift.
    
    Returns:
        (valid: bool, reason: str)
    """
    import difflib
    
    # 1. Must not be empty or identical
    if not rewritten or rewritten.strip() == "":
        return False, "empty_output"
    
    if rewritten.strip() == original.strip():
        return False, "no_change"
    
    # 2. Must be simple present tense
    if detect_verb_tense(rewritten) != "present":
        return False, "not_simple_present"
    
    # 3. Must preserve key modal / obligation terms
    for term in ["must", "shall", "required", "necessary"]:
        if term in original.lower() and term not in rewritten.lower():
            return False, "obligation_changed"
    
    # 4. Must not introduce significant new content
    orig_tokens = set(original.lower().split())
    new_tokens = set(rewritten.lower().split())
    added = new_tokens - orig_tokens
    
    # Allow common glue words only
    allowed_additions = {"and", "or", "then", "only", "after", "before", "the", "a", "an", "is", "are"}
    significant_additions = [t for t in added if t.isalpha() and len(t) > 2 and t not in allowed_additions]
    
    if len(significant_additions) > 3:
        return False, "new_content_introduced"
    
    # 5. Semantic similarity guard (cheap but effective)
    ratio = difflib.SequenceMatcher(None, original.lower(), rewritten.lower()).ratio()
    if ratio < 0.6:
        return False, "meaning_drift"
    
    return True, "ok"


# Main check function for rule integration
def check(sentence):
    """
    Main entry point for rule checking.
    
    Compatible with DocScanner rule system - receives either:
    - A string (plain sentence text)
    - A sentence object with .text attribute
    
    Returns list of issues found in the sentence.
    """
    issues = []
    
    # Handle both string and sentence object inputs
    if isinstance(sentence, str):
        sentence_text = sentence
        start_char = 0
        end_char = len(sentence)
    else:
        # Sentence object with attributes
        sentence_text = getattr(sentence, 'text', str(sentence))
        start_char = getattr(sentence, 'start_char', 0)
        end_char = getattr(sentence, 'end_char', len(sentence_text))
    
    # CRITICAL GATE 1: Check if this is even a sentence
    # Titles, headings, and fragments should NOT be analyzed
    if is_non_sentential(sentence_text):
        # Do NOT flag titles/headings - they don't need tense rules
        return issues  # Return empty - no issue to report
    
    # CRITICAL GATE 2: Check if this is metadiscourse
    # Structural sentences that introduce examples should NOT be rewritten
    if is_metadiscourse(sentence_text):
        # Do NOT flag metadiscourse - these are intentionally neutral
        return issues  # Return empty - no issue to report
    
    allowed, reason = can_convert_to_simple_present(sentence_text)
    
    # ============================================================
    # DECISION LOGIC: Classify based on context
    # ============================================================
    
    tense = detect_verb_tense(sentence_text)
    
    # Only analyze if not already in present tense
    if tense == "present":
        return issues  # Already correct, no issue
    
    # Context analysis
    classification = classify_sentence_for_tense(sentence_text)
    
    if not allowed:
        # DECISION: no_change - Preserve tense for good reasons
        if reason == "historical":
            issues.append({
                'text': sentence_text,
                'start': start_char,
                'end': end_char,
                'message': 'Past tense detected in historical context',
                'decision_type': 'no_change',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'Historical context preserved - past tense is appropriate when describing previous versions, design decisions, or events that occurred at a specific time. Converting to present would be factually incorrect.'
            })
        elif reason == "compliance_conditional":
            issues.append({
                'text': sentence_text,
                'start': start_char,
                'end': end_char,
                'message': 'Complex conditional requirement detected',
                'decision_type': 'explain',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'This sentence contains compliance language with conditions. Tense conversion could alter the logical relationship between conditions and requirements. Review manually to ensure accuracy.',
                'explanation': 'Conditional requirements with "must/shall... if/when" need careful review. The tense may be intentional to indicate specific timing or causality.'
            })
    else:
        # DECISION: rewrite - Safe to convert to simple present
        if tense == "future":
            issues.append({
                'text': sentence_text,
                'start': start_char,
                'end': end_char,
                'message': 'Future tense detected',
                'decision_type': 'rewrite',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'Technical documentation uses simple present tense for consistency and immediacy. Future tense ("will validate") should be converted to present ("validates") unless describing a planned future feature.',
                'ai_suggestion': None  # Will be filled by enrichment service
            })
        elif tense == "past":
            issues.append({
                'text': sentence_text,
                'start': start_char,
                'end': end_char,
                'message': 'Past tense detected',
                'decision_type': 'rewrite',
                'rule': 'simple_present_tense',
                'reviewer_rationale': 'Convert to simple present tense for consistency with technical documentation standards. Present tense makes instructions and descriptions more immediate and clear.',
                'ai_suggestion': None  # Will be filled by enrichment service
            })
    
    return issues
