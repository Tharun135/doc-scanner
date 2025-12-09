"""
Semantic Context System for Document-Level Understanding
=========================================================
This module builds a semantic map of the entire document to enable
context-aware AI suggestions that preserve meaning, coherence, and intent.

CRITICAL PRINCIPLE:
- Sentence-level checking = DETERMINISTIC (rules remain unchanged)
- Document-level understanding = CONTEXTUAL (AI uses document semantics)

This allows AI suggestions to:
- Understand what entities/products/terms exist in the document
- Track acronym expansions and usage patterns
- Resolve pronoun references (what "it", "this", "they" refer to)
- Maintain section context and topic continuity
- Preserve cross-sentence relationships

WITHOUT breaking your stable rule engine.

GOVERNANCE CONTRACT:
====================
The rewrite engine is SAFETY-GOVERNED.

It may only:
1. Resolve ambiguity (passive referent, pronoun, sequence)
2. Fix objective grammar errors (tense)
3. Address critical vague quantifiers

It must never:
1. Perform style-only or fluency-only rewrites
2. Rewrite without documented justification
3. Exceed 30% rewrite rate on typical documentation
4. Alter meaning or technical accuracy

Any change that increases rewrite rate or introduces new triggers
without governance review is considered a REGRESSION.

See: GOVERNANCE_CHECKLIST.md for enforcement procedures.
"""

from typing import List, Dict, Any, Optional, Set
import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Common technical writing patterns
ACRONYM_REGEX = r"\b[A-Z]{2,}\b"
ACRONYM_EXPANSION_PATTERN = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Z]{2,})\)"


@dataclass
class DocumentContext:
    """
    Semantic map of an entire document.
    
    This is built ONCE per document upload, then consulted by:
    - AI suggestion engine (for context-aware rewrites)
    - Acronym tracking rules (for first-use validation)
    - Consistency checking (for term usage patterns)
    """
    
    # Document identifier for telemetry
    doc_id: str = ""
    
    # Core document structure
    sentences: List[str] = field(default_factory=list)
    sections: Dict[int, str] = field(default_factory=dict)  # sentence_index -> section_title
    
    # Entity tracking (products, components, UI labels, protocols)
    entities: Dict[str, List[int]] = field(default_factory=dict)  # entity_text -> [sentence_indexes]
    
    # Acronym tracking with expansion context
    acronyms: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # acronym -> {first: idx, expanded: str, all_uses: [indexes]}
    
    # Topic and subject tracking
    sentence_topics: Dict[int, Optional[str]] = field(default_factory=dict)  # sentence_index -> main_noun
    
    # Pronoun resolution (simplified but effective)
    pronoun_links: Dict[int, Dict[str, Optional[str]]] = field(default_factory=dict)  # sentence_index -> {pronoun: referent}
    
    # Document metadata
    document_type: Optional[str] = None
    total_sentences: int = 0
    
    def get_sentence_context(self, sentence_index: int, window: int = 2) -> Dict[str, Any]:
        """
        Get comprehensive context for a specific sentence.
        
        Returns:
        - The sentence itself
        - Surrounding sentences (±window)
        - Section information
        - Active entities in this region
        - Acronyms used in this sentence
        - Pronoun references
        - Main topic/subject
        """
        if sentence_index < 0 or sentence_index >= len(self.sentences):
            return {}
        
        # Get surrounding sentences
        start_idx = max(0, sentence_index - window)
        end_idx = min(len(self.sentences), sentence_index + window + 1)
        
        context_sentences = []
        for i in range(start_idx, end_idx):
            if i == sentence_index:
                context_sentences.append(f"[CURRENT] {self.sentences[i]}")
            else:
                context_sentences.append(self.sentences[i])
        
        # Get current sentence
        current_sentence = self.sentences[sentence_index]
        
        # Find acronyms in this sentence
        acronyms_here = []
        for acronym, info in self.acronyms.items():
            if acronym in current_sentence:
                acronyms_here.append({
                    "acronym": acronym,
                    "expansion": info.get("expanded"),
                    "first_use_index": info.get("first"),
                    "is_first_use": info.get("first") == sentence_index
                })
        
        # Get entities mentioned in this sentence
        entities_here = []
        for entity, positions in self.entities.items():
            if sentence_index in positions:
                entities_here.append(entity)
        
        return {
            "sentence": current_sentence,
            "sentence_index": sentence_index,
            "section": self.sections.get(sentence_index, "Unknown"),
            "surrounding_sentences": context_sentences,
            "topic": self.sentence_topics.get(sentence_index),
            "acronyms": acronyms_here,
            "entities": entities_here,
            "pronoun_links": self.pronoun_links.get(sentence_index, {}),
            "window_start": start_idx,
            "window_end": end_idx
        }
    
    def get_acronym_context(self, acronym: str) -> Optional[Dict[str, Any]]:
        """Get full context for a specific acronym."""
        return self.acronyms.get(acronym)
    
    def is_acronym_already_expanded(self, acronym: str, current_index: int) -> bool:
        """Check if an acronym has been expanded before the current position."""
        info = self.acronyms.get(acronym)
        if not info:
            return False
        
        first_use = info.get("first", float('inf'))
        return first_use < current_index and info.get("expanded") is not None


def build_document_context(
    sentences: List[str],
    sections: Optional[Dict[int, str]] = None,
    nlp = None,
    document_type: Optional[str] = None,
    doc_id: str = "unknown"
) -> DocumentContext:
    """
    Build a semantic map of the entire document.
    
    This is the SINGLE ENTRY POINT for context building.
    Called once per document upload, before any analysis.
    
    Args:
        sentences: List of sentence strings
        sections: Optional mapping of sentence_index -> section_title
        nlp: Optional spaCy nlp model (if available)
        document_type: Optional document type hint
        doc_id: Document identifier for telemetry
        
    Returns:
        DocumentContext object with full semantic map
    """
    logger.info(f"🧠 Building semantic context for document ({len(sentences)} sentences)")
    
    ctx = DocumentContext()
    ctx.doc_id = doc_id
    ctx.sentences = sentences
    ctx.sections = sections or {}
    ctx.document_type = document_type
    ctx.total_sentences = len(sentences)
    # Track active subject across sentences for pronoun resolution
    last_subject = None
    
    for idx, text in enumerate(sentences):
        # Use spaCy if available for better analysis
        if nlp:
            doc = nlp(text)
            
            # 1) Extract entities (using spaCy NER)
            for ent in doc.ents:
                ctx.entities.setdefault(ent.text, []).append(idx)
            
            # 2) Extract TitleCase terms (likely product names, UI labels)
            for token in doc:
                # TitleCase: First letter uppercase, rest lowercase (e.g., "Controller", "Asset")
                if token.text and len(token.text) > 1:
                    if token.text[0].isupper() and any(c.islower() for c in token.text[1:]):
                        # Skip common words
                        if token.text.lower() not in {'the', 'this', 'that', 'these', 'those', 'you', 'your'}:
                            ctx.entities.setdefault(token.text, []).append(idx)
            
            # 3) Extract main subject/topic
            main_noun = None
            for token in doc:
                # Find subject (nsubj = nominal subject, nsubjpass = passive nominal subject)
                if token.dep_ in ("nsubj", "nsubjpass") and token.pos_ in ("NOUN", "PROPN"):
                    main_noun = token.text
                    last_subject = token.text  # Update active subject
                    break
            
            # If no subject found, use first noun
            if not main_noun:
                for token in doc:
                    if token.pos_ in ("NOUN", "PROPN"):
                        main_noun = token.text
                        last_subject = token.text
                        break
            
            ctx.sentence_topics[idx] = main_noun
            
            # 4) Pronoun resolution (simple but effective)
            for token in doc:
                if token.pos_ == "PRON" and token.text.lower() in ("it", "they", "this", "that"):
                    # Link pronoun to last known subject
                    ctx.pronoun_links.setdefault(idx, {})[token.text.lower()] = last_subject
        
        else:
            # Fallback: basic regex-based extraction when spaCy unavailable
            # Extract nouns (crude: words starting with capital or common nouns)
            words = text.split()
            
            # Find subject (first capitalized noun or common technical noun)
            subject = None
            for word in words[:5]:  # Check first few words
                clean_word = word.strip('.,;:!?')
                if clean_word and (clean_word[0].isupper() or clean_word.lower() in ['controller', 'system', 'device', 'network', 'server', 'client']):
                    if clean_word.lower() not in {'the', 'a', 'an', 'this', 'that', 'it'}:
                        subject = clean_word
                        last_subject = clean_word
                        break
            
            ctx.sentence_topics[idx] = subject
            
            # Pronoun resolution (fallback)
            text_lower = text.lower()
            pronouns = ['it', 'this', 'that', 'they']
            for pronoun in pronouns:
                if f' {pronoun} ' in f' {text_lower} ':
                    ctx.pronoun_links.setdefault(idx, {})[pronoun] = last_subject
        
        # 5) Acronym detection and expansion tracking
        # Find expanded acronyms: "Full Term (ACRO)"
        for match in re.finditer(ACRONYM_EXPANSION_PATTERN, text):
            expansion = match.group(1).strip()
            acronym = match.group(2).strip()
            
            if acronym not in ctx.acronyms:
                ctx.acronyms[acronym] = {
                    "first": idx,
                    "expanded": expansion,
                    "all_uses": [idx]
                }
            else:
                ctx.acronyms[acronym]["all_uses"].append(idx)
        
        # Find standalone acronyms (not in expansion context)
        for match in re.finditer(ACRONYM_REGEX, text):
            acronym = match.group(0)
            
            # Skip if already found with expansion
            if acronym in ctx.acronyms:
                if idx not in ctx.acronyms[acronym]["all_uses"]:
                    ctx.acronyms[acronym]["all_uses"].append(idx)
            else:
                # First occurrence without expansion
                ctx.acronyms[acronym] = {
                    "first": idx,
                    "expanded": None,  # Not expanded
                    "all_uses": [idx]
                }
    
    logger.info(f"✅ Semantic context built: {len(ctx.entities)} entities, {len(ctx.acronyms)} acronyms tracked")
    
    return ctx


def get_context_for_ai_suggestion(
    sentence_index: int,
    ctx: DocumentContext,
    issue_type: Optional[str] = None
) -> str:
    """
    Build a context string to pass to AI suggestion engine.
    
    This converts the structured semantic map into a natural language
    context description that the LLM can understand.
    
    Args:
        sentence_index: Index of the sentence being improved
        ctx: DocumentContext object
        issue_type: Optional type of issue (e.g., "tense", "passive voice", "acronym")
        
    Returns:
        Formatted context string for LLM prompt
    """
    context_data = ctx.get_sentence_context(sentence_index, window=2)
    
    if not context_data:
        return ""
    
    # Build context prompt sections
    parts = []
    
    # Section context
    if context_data.get("section"):
        parts.append(f"Section: {context_data['section']}")
    
    # Surrounding sentences for flow context
    if context_data.get("surrounding_sentences"):
        parts.append("Context:")
        for sent in context_data["surrounding_sentences"]:
            parts.append(f"  {sent}")
    
    # Main topic
    if context_data.get("topic"):
        parts.append(f"Main subject: {context_data['topic']}")
    
    # Acronyms in use
    if context_data.get("acronyms"):
        acronym_info = []
        for acro in context_data["acronyms"]:
            if acro["expansion"]:
                if acro["is_first_use"]:
                    acronym_info.append(f"{acro['acronym']} (first use, expanded as '{acro['expansion']}')")
                else:
                    acronym_info.append(f"{acro['acronym']} (already expanded as '{acro['expansion']}' earlier)")
            else:
                acronym_info.append(f"{acro['acronym']} (not yet expanded)")
        
        if acronym_info:
            parts.append("Acronyms: " + ", ".join(acronym_info))
    
    # Entities/products mentioned
    if context_data.get("entities"):
        parts.append(f"Key terms: {', '.join(context_data['entities'][:5])}")
    
    # Pronoun references
    if context_data.get("pronoun_links"):
        pronoun_info = []
        for pronoun, referent in context_data["pronoun_links"].items():
            if referent:
                pronoun_info.append(f"'{pronoun}' refers to '{referent}'")
        
        if pronoun_info:
            parts.append("References: " + ", ".join(pronoun_info))
    
    return "\n".join(parts)


def format_context_for_llm_prompt(
    sentence: str,
    context_str: str,
    issue_type: Optional[str] = None,
    feedback_text: Optional[str] = None
) -> str:
    """
    Format the complete prompt for LLM with context.
    
    This is the CRITICAL PROMPT that prevents meaning drift.
    """
    
    prompt_parts = [
        "You are improving technical documentation while preserving exact meaning.",
        "",
        "ABSOLUTE CONSTRAINTS - VIOLATION = REJECT:",
        "1. Do NOT merge multiple sentences into one",
        "2. Do NOT reorder events or change sequence",
        "3. Do NOT replace specific terms with generic terms (e.g., 'controller' → 'system')",
        "4. Do NOT remove temporal markers ('then', 'after', 'before')",
        "5. If sentence contains a pronoun ('it', 'this', 'they'), replace with explicit subject from context",
        "6. CRITICAL: If an acronym was already defined earlier in this document, you MUST NOT expand it again",
        "",
        "STYLE REQUIREMENTS:",
        "1. Use ONLY simple present tense (e.g., 'connects', 'displays', 'shows')",
        "2. Use active voice (subject performs action)",
        "3. Keep ALL product names, acronyms, and technical terms EXACTLY as written",
        "4. Do NOT change or remove any numbers, measurements, or specifications",
        "",
        "DOCUMENT CONTEXT:",
        context_str,
        "",
        "CURRENT SENTENCE:",
        sentence,
    ]
    
    if issue_type:
        prompt_parts.append(f"\nISSUE TYPE: {issue_type}")
    
    if feedback_text:
        prompt_parts.append(f"SPECIFIC ISSUE: {feedback_text}")
    
    prompt_parts.extend([
        "",
        "TASK: Fix ONLY the specific issue while preserving all other aspects.",
        "Do NOT be creative. Do NOT improve flow. Do NOT condense.",
        "If unsure, return the sentence UNCHANGED.",
        "Return ONLY the rewritten sentence, nothing else."
    ])
    
    return "\n".join(prompt_parts)


def can_be_rewritten(sentence: str, sentence_index: int, ctx: DocumentContext) -> bool:
    """
    Eligibility gate: Determine if sentence is allowed to be rewritten.
    
    Prevents LLM from touching sentences that should never be modified.
    This is evaluated BEFORE calling LLM, not after.
    
    Returns False if sentence contains:
    - Acronym that is not first occurrence
    - Sequence operators (then, after, before, etc.)
    - Unbound pronouns
    """
    import re
    
    sentence_lower = sentence.lower()
    
    # Rule 1: Acronym not at first occurrence -> no rewrite
    acronyms_in_sentence = set(re.findall(r'\b[A-Z]{2,}\b', sentence))
    for acronym in acronyms_in_sentence:
        if acronym in ctx.acronyms:
            first_use = ctx.acronyms[acronym].get('first', float('inf'))
            if sentence_index != first_use:
                return False  # Acronym already defined - do not rewrite
    
    # Rule 2: Sequence operators -> no rewrite (too risky)
    sequence_operators = ['then', 'after', 'before', 'once', 'during', 'when', 'while']
    for operator in sequence_operators:
        if f' {operator} ' in f' {sentence_lower} ' or sentence_lower.startswith(f'{operator} '):
            return False  # Sequence carrier - preserve exactly
    
    # Rule 3: Unbound pronoun -> no rewrite (no known referent)
    pronouns = ['it', 'this', 'that', 'these', 'those', 'they']
    for pronoun in pronouns:
        if f' {pronoun} ' in f' {sentence_lower} ' or sentence_lower.startswith(f'{pronoun} '):
            # Check if pronoun has known referent
            pronoun_links = ctx.pronoun_links.get(sentence_index, {})
            if pronoun not in pronoun_links or not pronoun_links.get(pronoun):
                return False  # Unbound pronoun - cannot safely rewrite
    
    return True  # Sentence is eligible for rewriting


def rewrite_required(sentence: str, sentence_index: int, ctx: DocumentContext, issue_type: Optional[str] = None) -> tuple[bool, str]:
    """
    Justification gate: Determine if rewrite is NECESSARY, not just allowed.
    
    Returns (True, reason) only if sentence has mandatory correction triggers:
    - Pronoun ambiguity: pronoun without clear antecedent in context map
    - Acronym first-use: first occurrence requiring expansion
    - UI duplication: UI element label appears twice without markup
    - Sequence fuzz: technical order inference unclear
    - Safety deviation: CAUTION/WARNING phrasing inconsistent
    
    Does NOT justify rewrites for:
    - Style improvements
    - Fluency optimization  
    - Readability enhancement
    - Better phrasing
    
    Returns:
        (bool, str): (is_required, justification_reason)
    """
    import re
    
    sentence_lower = sentence.lower()
    
    # If no issue type specified, check for intrinsic mandatory triggers only
    if not issue_type or issue_type.lower() in ['general', 'general review', 'grammar check']:
        # No detected defect = no rewrite justification
        return (False, "no_issue_detected")
    
    # Issue-type specific validation - must validate issue actually exists
    issue_lower = issue_type.lower()
    
    # Trigger 1: Pronoun ambiguity (MANDATORY: referent unclear)
    if 'antecedent' in issue_lower or 'pronoun' in issue_lower:
        pronouns_pattern = r'\b(it|this|that)\b'
        pronoun_matches = list(re.finditer(pronouns_pattern, sentence_lower))
        
        for match in pronoun_matches:
            pronoun = match.group(1)
            pronoun_links = ctx.pronoun_links.get(sentence_index, {})
            
            if pronoun not in pronoun_links or not pronoun_links.get(pronoun):
                return (True, "pronoun_ambiguity")
        
        # Issue flagged but no actual ambiguity found
        return (False, "pronoun_resolved")
    
    # Trigger 2: Passive voice (ONLY if causing referent confusion)
    if 'passive' in issue_lower:
        passive_indicators = [' is ', ' are ', ' was ', ' were ', ' been ']
        has_passive = any(indicator in f' {sentence_lower} ' for indicator in passive_indicators)
        
        if not has_passive:
            return (False, "no_passive_detected")
        
        # Check if passive causes ambiguity
        has_by_phrase = ' by ' in sentence_lower
        if has_by_phrase:
            return (False, "passive_actor_clear")
        
        # Check if subject is clear from sentence start
        if sentence.strip().startswith(('The system', 'The device', 'The controller', 'The module', 'The software')):
            return (False, "passive_subject_clear")
        
        # Passive with unclear actor - rewrite justified
        return (True, "passive_referent_unclear")
    
    # Trigger 3: Vague terms (ONLY critical vagueness requiring specificity)
    if 'vague' in issue_lower or 'unclear' in issue_lower:
        critical_vague = ['some', 'various', 'several', 'many']
        has_critical_vague = any(f' {term} ' in f' {sentence_lower} ' for term in critical_vague)
        
        if has_critical_vague:
            return (True, "vague_quantifier")
        
        return (False, "no_vagueness_detected")
    
    # Trigger 4: Tense issues (grammar correctness - MANDATORY)
    if 'tense' in issue_lower:
        return (True, "grammar_tense_error")
    
    # All other issue types are style/optimization - NOT justified
    # Block: adverb overuse, long sentences, complex sentences, redundant phrases, modal fluff, inappropriate tone
    style_keywords = ['adverb', 'long sentence', 'complex', 'redundant', 'modal', 'tone', 'fluency', 'readability']
    if any(kw in issue_lower for kw in style_keywords):
        return (False, "style_not_justified")
    
    # Default: No justification for rewrite
    return (False, "no_trigger_found")

    """
    Justification gate: Determine if rewrite is NECESSARY, not just allowed.
    
    Returns True only if sentence has clear quality defects:
    - Ambiguity (vague referents, unclear subject)
    - Reference confusion (pronoun without clear antecedent)
    - Missing subject (passive without clear actor)
    - Procedural clarity issue (action steps unclear)
    - UI element mislabeling
    
    Does NOT justify rewrites for:
    - Style improvements
    - Fluency optimization
    - Simplification
    - Paraphrasing
    
    This is Gate 2: Rewrite only when needed, not when allowed.
    """
    import re
    
    sentence_lower = sentence.lower()
    
    # If no issue type specified, require intrinsic defect evidence
    if not issue_type or issue_type.lower() in ['general', 'general review', 'grammar check']:
        # Look for objective defects only
        
        # Defect 1: Vague quantifiers without specificity
        critical_vague = ['some', 'various', 'several', 'many']
        has_critical_vague = any(f' {term} ' in f' {sentence_lower} ' for term in critical_vague)
        
        # Defect 2: Ambiguous pronoun (pronoun without clear antecedent)
        pronouns_pattern = r'\b(it|this|that)\b'
        pronoun_matches = list(re.finditer(pronouns_pattern, sentence_lower))
        
        for match in pronoun_matches:
            pronoun = match.group(1)
            pronoun_links = ctx.pronoun_links.get(sentence_index, {})
            
            if pronoun not in pronoun_links or not pronoun_links.get(pronoun):
                # Ambiguous pronoun - genuine defect
                return True
        
        # Defect 3: Passive voice with unclear actor (starts with "It is" or "This is" + passive)
        passive_unclear = sentence.strip().startswith(('It is ', 'It was ', 'This is ', 'This was '))
        if passive_unclear and (' configured' in sentence_lower or ' performed' in sentence_lower or ' done' in sentence_lower):
            return True  # Passive with weak subject
        
        # No intrinsic defect found - block rewrite
        if not has_critical_vague:
            return False
    
    # Issue-type specific validation
    if issue_type:
        issue_lower = issue_type.lower()
        
        # Passive voice - validate that problematic passive actually exists
        if 'passive' in issue_lower:
            passive_indicators = [' is ', ' are ', ' was ', ' were ', ' been ']
            has_passive = any(indicator in f' {sentence_lower} ' for indicator in passive_indicators)
            
            if not has_passive:
                return False  # Issue type incorrect - no passive voice
            
            # Check if passive is problematic (unclear actor)
            has_by_phrase = ' by ' in sentence_lower
            if has_by_phrase:
                return False  # "is configured by user" is clear - no rewrite needed
            
            # Check if subject is clear from context
            if sentence.strip().startswith(('The system', 'The device', 'The controller', 'The module')):
                return False  # Clear subject - passive acceptable in tech docs
            
            # Passive with unclear actor - rewrite justified
            return True
        
        # Vague terms - validate vagueness actually exists
        if 'vague' in issue_lower or 'unclear' in issue_lower:
            vague_terms = ['some', 'various', 'several', 'many', 'often', 'usually']
            has_vague = any(f' {term} ' in f' {sentence_lower} ' for term in vague_terms)
            return has_vague  # Only rewrite if actually vague
        
        # Tense issues - grammar correctness (always justified)
        if 'tense' in issue_lower:
            return True
        
        # Unclear antecedents - pronoun issues (always justified if flagged)
        if 'antecedent' in issue_lower:
            return True
        
        # Style issues - NOT justified for technical docs
        if any(style in issue_lower for style in ['adverb', 'long sentence', 'complex', 'redundant', 'modal', 'tone']):
            return False  # Style improvements not justified
    
    # Default: No justification
    return False


def change_alters_meaning(original: str, suggestion: str, ctx: DocumentContext, sentence_index: Optional[int] = None) -> bool:
    """
    Hard stop: Reject suggestion if it corrupts meaning.
    
    This is a safety net against LLM hallucination and creativity.
    Better to return original than to output nonsense.
    """
    if not suggestion or not original:
        return True
    
    original_lower = original.lower()
    suggestion_lower = suggestion.lower()
    
    # Extract key nouns from original (crude but effective)
    import re
    original_nouns = set(re.findall(r'\b(controller|system|network|session|firmware|device|component|server|client|interface|connector|module)\b', original_lower))
    suggestion_nouns = set(re.findall(r'\b(controller|system|network|session|firmware|device|component|server|client|interface|connector|module)\b', suggestion_lower))
    
    # Rule 1: Subject enforcement - specific technical nouns must not disappear
    if original_nouns and not original_nouns.intersection(suggestion_nouns):
        return True  # Specific subject replaced with generic or removed
    
    # Rule 2: Temporal marker enforcement
    temporal_markers = ['then', 'after', 'before', 'next', 'first', 'finally']
    for marker in temporal_markers:
        if marker in original_lower and marker not in suggestion_lower:
            return True  # Event sequence lost
    
    # Rule 3: Merge detection - sentence got significantly longer (merged with something)
    if len(suggestion.split()) > len(original.split()) * 1.5:
        return True  # Likely merged or added content
    
    # Rule 4: Pronoun resolution is ALLOWED if referent matches context
    pronouns = ['it', 'this', 'that', 'these', 'those', 'they']
    original_has_pronoun = any(f' {p} ' in f' {original_lower} ' or original_lower.startswith(f'{p} ') for p in pronouns)
    suggestion_has_pronoun = any(f' {p} ' in f' {suggestion_lower} ' or suggestion_lower.startswith(f'{p} ') for p in pronouns)
    
    if original_has_pronoun and not suggestion_has_pronoun:
        # Pronoun was resolved - check if resolution is valid
        if ctx and sentence_index is not None and pronoun_resolved_correctly(original, suggestion, ctx, sentence_index):
            return False  # Valid pronoun resolution - allow
    
    if original_has_pronoun and suggestion_has_pronoun:
        return True  # Pronoun not resolved when it should be
    
    # Rule 5: Acronym expansion FORBIDDEN if already defined
    if ctx and sentence_index is not None:
        if acronym_expansion_added(original, suggestion, ctx, sentence_index):
            return True  # Illegal acronym expansion
    
    # Rule 6: Critical terms must not be replaced with synonyms
    critical_pairs = [
        ('restart', 'reboot'),
        ('re-establish', 'reconnect'),
        ('session', 'connection'),
    ]
    for orig_term, syn_term in critical_pairs:
        if orig_term in original_lower and orig_term not in suggestion_lower and syn_term in suggestion_lower:
            return True  # Technical term replaced with less precise synonym
    
    return False  # Suggestion appears safe


def pronoun_resolved_correctly(original: str, suggestion: str, ctx: DocumentContext, sentence_index: int) -> bool:
    """
    Check if pronoun resolution is valid.
    
    Valid if:
    - Pronoun in original maps to known referent in context
    - Suggestion inserts that same referent
    - Event order remains intact
    """
    pronoun_links = ctx.pronoun_links.get(sentence_index, {})
    
    if not pronoun_links:
        return False  # No known referent
    
    # Check if any known referent appears in suggestion
    for pronoun, referent in pronoun_links.items():
        if referent and referent.lower() in suggestion.lower():
            # Referent was inserted - this is valid clarification
            return True
    
    return False


def acronym_expansion_added(original: str, suggestion: str, ctx: DocumentContext, sentence_index: int) -> bool:
    """
    Detect if suggestion illegally expanded an acronym.
    
    Returns True if expansion was added where it shouldn't be.
    """
    import re
    
    # Find acronyms in original
    acronyms_in_original = set(re.findall(r'\b[A-Z]{2,}\b', original))
    
    if not acronyms_in_original:
        return False  # No acronyms to expand
    
    for acronym in acronyms_in_original:
        if acronym in ctx.acronyms:
            acro_info = ctx.acronyms[acronym]
            first_use = acro_info.get('first', float('inf'))
            expansion = acro_info.get('expanded', '')
            
            # If this is NOT the first use, expansion is forbidden
            if sentence_index != first_use and expansion:
                # Check if expansion appears in suggestion but not in original
                if expansion.lower() in suggestion.lower() and expansion.lower() not in original.lower():
                    return True  # Illegal expansion added
    
    return False
