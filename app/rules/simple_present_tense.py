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
    logging.debug(f"RAG helper not available for {__name__} - using basic rules") 96cc86a16e63ddab59591eb3e60015e1d0b5ea16
# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule 1: Check for future tense constructions (will + verb)
    for token in doc:
        if token.text.lower() == "will" and token.dep_ == "aux":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.pos_ == "VERB":
                sentence = token.sent.text.strip()
                if not _is_conditional_or_example(sentence):
                    suggestions.append(f"Consider using simple present tense instead of future tense. Replace 'will {next_token.text}' with '{next_token.text}' or '{_get_present_form(next_token.text)}'.")
    
    # Rule 2: Check for continuous tense (be + ing verbs)
    for token in doc:
        if token.lemma_ == "be" and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.tag_ == "VBG":  # Present participle (-ing form)
                sentence = token.sent.text.strip()
                if not _is_ongoing_action_context(sentence) and not _is_state_or_requirement_context(sentence, next_token.text):
                    base_verb = _get_present_form(next_token.lemma_)
                    suggestions.append(f"Consider using simple present tense instead of continuous tense. Replace '{token.text} {next_token.text}' with '{base_verb}'.")
    
    # Rule 3: Check for perfect tense constructions (have/has + past participle)
    for token in doc:
        if token.lemma_ == "have" and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.tag_ == "VBN":  # Past participle
                sentence = token.sent.text.strip()
                if not _is_experience_or_result_context(sentence):
                    base_verb = _get_present_form(next_token.lemma_)
                    suggestions.append(f"Consider using simple present tense instead of perfect tense. Replace '{token.text} {next_token.text}' with '{base_verb}'.")

    return suggestions if suggestions else []

def _is_narrative_or_example(sentence):
    """Check if sentence is describing past events, stories, or examples"""
    narrative_indicators = ["yesterday", "last", "ago", "in the past", "previously", "earlier", "once upon", "example:", "for instance"]
    return any(indicator in sentence.lower() for indicator in narrative_indicators)

def _is_conditional_or_example(sentence):
    """Check if sentence contains conditional or hypothetical language"""
    conditional_indicators = ["if", "when", "unless", "suppose", "imagine", "example", "scenario"]
    return any(indicator in sentence.lower() for indicator in conditional_indicators)

def _is_ongoing_action_context(sentence):
    """Check if continuous tense is appropriate (ongoing actions)"""
    ongoing_indicators = ["currently", "now", "at the moment", "right now", "while", "during"]
    return any(indicator in sentence.lower() for indicator in ongoing_indicators)

def _is_state_or_requirement_context(sentence, verb):
    """Check if continuous tense describes a required state or condition"""
    sentence_lower = sentence.lower()
    verb_lower = verb.lower()
    
    # State/status verbs that often describe conditions rather than actions
    state_verbs = ["running", "working", "operating", "functioning", "executing", 
                   "active", "processing", "connecting", "monitoring", "listening",
                   "waiting", "pending", "loading", "installing", "updating"]
    
    # Context indicators for requirements/states/conditions
    requirement_indicators = [
        "requirement", "ensure", "verify", "check", "confirm", "must be",
        "should be", "needs to be", "has to be", "required", "necessary",
        "prerequisite", "condition", "status", "state"
    ]
    
    # System/service/component contexts where continuous tense describes state
    system_contexts = [
        "service", "server", "system", "application", "connector", "component",
        "module", "process", "daemon", "agent", "driver", "engine", "instance"
    ]
    
    # Check if it's a state verb
    if verb_lower in state_verbs:
        # Check for requirement/state context
        if any(indicator in sentence_lower for indicator in requirement_indicators):
            return True
        
        # Check for system/service context
        if any(context in sentence_lower for context in system_contexts):
            return True
    
    # Check for specific patterns that indicate states/requirements
    state_patterns = [
        r'\b(connector|service|system|server|application|component|module|process)\b.*\bis\s+' + verb_lower,
        r'\brequire.*\bis\s+' + verb_lower,
        r'\bensure.*\bis\s+' + verb_lower,
        r'\bmust\s+be\s+' + verb_lower,
        r'\bneeds?\s+to\s+be\s+' + verb_lower
    ]
    
    for pattern in state_patterns:
        if re.search(pattern, sentence_lower):
            return True
    
    return False

def _is_experience_or_result_context(sentence):
    """Check if perfect tense is appropriate (experience or completed actions with present relevance)"""
    experience_indicators = ["ever", "never", "already", "just", "recently", "so far", "until now", "experience"]
    return any(indicator in sentence.lower() for indicator in experience_indicators)

def _has_explicit_agent(sentence):
    """Check if passive sentence has an explicit agent (by someone/something)"""
    return " by " in sentence.lower()

def _get_present_form(verb):
    """Get the simple present form of a verb"""
    # Simple mapping for common irregular verbs
    irregular_verbs = {
        "was": "is", "were": "are", "been": "is", "had": "has", "did": "does",
        "went": "goes", "came": "comes", "took": "takes", "made": "makes",
        "said": "says", "got": "gets", "saw": "sees", "knew": "knows",
        "thought": "thinks", "found": "finds", "gave": "gives", "told": "tells",
        "worked": "works", "looked": "looks", "used": "uses", "wanted": "wants",
        "called": "calls", "asked": "asks", "tried": "tries", "needed": "needs"
    }
    
    verb_lower = verb.lower()
    
    # Check irregular verbs first
    if verb_lower in irregular_verbs:
        return irregular_verbs[verb_lower]
    
    # Handle regular past tense (-ed endings)
    if verb_lower.endswith("ed"):
        # Remove -ed ending
        base = verb_lower[:-2]
        # Handle doubled consonants (e.g., "stopped" -> "stop")
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] in "bcdfghjklmnpqrstvwxyz":
            base = base[:-1]
        return base
    
    # Handle -ing endings (present participle)
    if verb_lower.endswith("ing"):
        base = verb_lower[:-3]
        # Handle doubled consonants
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] in "bcdfghjklmnpqrstvwxyz":
            base = base[:-1]
        # Handle dropped 'e' (e.g., "making" -> "make")
        elif not base.endswith("e") and len(base) >= 2:
            # Check if we need to add 'e' back
            if base[-1] in "cglnrsz" and base[-2] not in "aeiou":
                base += "e"
        return base
    
    # Return as-is if no transformation needed
    return verb

