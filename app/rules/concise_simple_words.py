import re
from .spacy_utils import get_nlp_model
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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = get_nlp_model()

def check(content):
    suggestions = []

    # Strip HTML tags from content and decode HTML entities
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Define doc using nlp
    doc = nlp(text_content)
    """
    MSTP Guidance:
    1. Replace overly formal/verbose phrases with concise, simple alternatives.
    2. Detect unnecessary modifiers (e.g., 'very', 'quite', 'easily').
    3. Flag weak or vague verbs (e.g., 'be', 'have').
    4. Highlight ambiguous words that can confuse context (e.g., 'file', 'post', 'mark').
    """

    # 1. Replace overly formal or verbose phrases
    formal_phrases = {
        r"\butilize\b": "use",
        r"\bmake use of\b": "use",
        r"\bextract\b": "remove",
        r"\beliminate\b": "remove",
        r"\bin order to\b": "to",
        r"\bas a means to\b": "to",
        r"\bestablish connectivity\b": "connect",
        r"\blet know\b": "tell",
        r"\binform\b": "tell",
        r"\bin addition\b": "also",
        r"\bquite\b": "",  # Suggest removal
        r"\bvery\b": "",   # Suggest removal
    }

    for pattern, replacement in formal_phrases.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            # Find the sentence containing this phrase
            containing_sentence = ""
            for sent in doc.sents:
                if found_text.lower() in sent.text.lower():
                    containing_sentence = sent.text.strip()
                    break
            
            if replacement:
                suggestions.append(f"Issue: Verbose or formal phrase detected - replace '{found_text}' with '{replacement}' for simplicity")
            else:
                suggestions.append(f"Issue: Unnecessary modifier detected - consider removing '{found_text}' as it may not add value")

    # 2. Detect unnecessary modifiers and intensifiers (expanded list)
    intensifiers_and_modifiers = r"\b(very|quite|rather|fairly|pretty|really|truly|extremely|incredibly|absolutely|definitely|certainly|obviously|clearly|simply|just|merely|only|easily|effectively|quickly)\s+(\w+)"
    matches = re.finditer(intensifiers_and_modifiers, text_content, flags=re.IGNORECASE)
    for match in matches:
        modifier = match.group(1)
        word = match.group(2)
        # Skip if the modifier is essential (e.g., "only one", "just started")
        if modifier.lower() in ['only', 'just'] and word.lower() in ['one', 'two', 'started', 'finished', 'completed']:
            continue
        # Skip "effectively with" as it's often appropriate in technical contexts
        if modifier.lower() == 'effectively' and word.lower() == 'with':
            continue
        # Skip other context-appropriate combinations
        if modifier.lower() == 'simply' and word.lower() in ['by', 'using', 'with']:
            continue
        suggestions.append(f"Consider removing unnecessary modifier: '{modifier} {word}' → '{word}' or use a stronger word.")

    # 3. Expanded weak verb constructions with context awareness
    weak_verb_patterns = [
        # Only flag "there are" when it's truly weak, not when introducing lists
        (r"\bthere are\s+(?!no\s|not\s|zero\s|two\s|three\s|four\s|five\s|six\s|seven\s|eight\s|nine\s|ten\s|several\s|multiple\s|many\s|few\s|\d+\s)\w+", "list the items directly"),  # Exclude numbered/quantified lists
        (r"\bthere is\s+a\s+(?!not\s)\w+", "state directly"),  # Exclude negative constructions  
        (r"\bit is important to\b", "'must' or 'should'"),
        (r"\bit is possible to\b", "'can' or 'may'"),
        (r"\bit is necessary to\b", "'must' or 'need to'"),
        (r"\bhave the ability to\b", "'can'"),
        (r"\bhave the option to\b", "'can' or 'may'"),
        (r"\bare able to\b", "'can'"),
        (r"\bmake use of\b", "'use'"),
        (r"\btake advantage of\b", "'use' or 'leverage'"),
        (r"\bprovide assistance\b", "'help' or 'assist'"),
        (r"\bperform an analysis\b", "'analyze'"),
        (r"\bconduct a review\b", "'review'"),
        (r"\bmake a decision\b", "'decide'"),
        (r"\bgive consideration to\b", "'consider'"),
        (r"\bhas the capability\b", "'can'"),
    ]
    
    for pattern, suggestion in weak_verb_patterns:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            
            # Additional context check for "there are" constructions
            if found_text.lower().startswith("there are"):
                # Get the context around the match to check for list introduction patterns
                start_pos = match.start()
                end_pos = match.end()
                context_after = text_content[end_pos:end_pos+50].lower()
                
                # Don't flag if it's followed by list introduction patterns
                if any(indicator in context_after for indicator in [
                    ":", "ways to", "methods to", "options", "steps", "approaches",
                    "techniques", "strategies", "features", "benefits", "reasons"
                ]):
                    continue
                    
                # Don't flag if it contains specific quantifiers or numbers
                if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|several|multiple|many|\d+)\b", found_text, re.IGNORECASE):
                    continue
            
            suggestions.append(f"Weak verb construction: Replace '{found_text}' with {suggestion} for directness.")

    # 4. Nominalizations (turning verbs into nouns)
    nominalizations = {
        r"\bmake an assessment\b": "assess",
        r"\bmake an assumption\b": "assume", 
        r"\bmake a calculation\b": "calculate",
        r"\bmake a comparison\b": "compare",
        r"\bmake a determination\b": "determine",
        r"\bmake an evaluation\b": "evaluate",
        r"\bmake an implementation\b": "implement",
        r"\bmake an investigation\b": "investigate",
        r"\bmake a recommendation\b": "recommend",
        r"\bmake a suggestion\b": "suggest",
        r"\bperform an analysis\b": "analyze",
        r"\bperform testing\b": "test",
        r"\bconduct research\b": "research",
        r"\btake action\b": "act",
    }
    
    for pattern, replacement in nominalizations.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            suggestions.append(f"Nominalization: Replace '{found_text}' with '{replacement}' for conciseness.")

    # 5. Wordy prepositional phrases
    wordy_phrases = {
        r"\bwith the exception of\b": "except",
        r"\bwith the purpose of\b": "to",
        r"\bfor the purpose of\b": "to", 
        r"\bin the majority of cases\b": "usually",
        r"\bin most instances\b": "usually",
        r"\bon a regular basis\b": "regularly",
        r"\bon a daily basis\b": "daily",
        r"\bat the present moment\b": "now",
        r"\bin the near future\b": "soon",
        r"\bat this point in time\b": "now",
        r"\bdue to the fact that\b": "because",
        r"\bin spite of the fact that\b": "although",
        r"\bin the event that\b": "if",
        r"\bin the case that\b": "if",
    }
    
    for pattern, replacement in wordy_phrases.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            suggestions.append(f"Wordy phrase: Replace '{found_text}' with '{replacement}'.")

    # 6. Redundant word pairs
    redundant_pairs = [
        r"\bfree gift\b",
        r"\bendorse or approve\b", 
        r"\bunited together\b",
        r"\bconnect together\b",
        r"\bmix together\b",
        r"\bplan ahead\b",
        r"\badvance planning\b",
        r"\bfuture plans\b",
        r"\bpast history\b",
        r"\bpresent status\b",
        r"\brepeat again\b",
        r"\breturn back\b",
        r"\brevert back\b",
    ]
    
    for pattern in redundant_pairs:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            # Suggest keeping just the essential word
            essential_word = found_text.split()[-1] if ' ' in found_text else found_text
            suggestions.append(f"Redundant pair: '{found_text}' → '{essential_word}'")

    return suggestions if suggestions else []