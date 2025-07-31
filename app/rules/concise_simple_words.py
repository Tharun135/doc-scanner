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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

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

    # 2. Detect unnecessary adverbs
    unnecessary_adverbs = r"\b(very|quite|easily|effectively|quickly)\b"
    matches = re.finditer(unnecessary_adverbs, text_content, flags=re.IGNORECASE)
    for match in matches:
        found_text = match.group()
        # Find the sentence containing this adverb
        containing_sentence = ""
        for sent in doc.sents:
            if found_text.lower() in sent.text.lower():
                containing_sentence = sent.text.strip()
                break
        
        suggestions.append(f"Issue: Unnecessary adverb detected - consider removing the adverb '{found_text}' unless it is essential for meaning")

    # 3. Flag potentially weak verb constructions (more nuanced approach)
    # Focus on specific weak patterns rather than all "be" and "have" verbs
    weak_verb_patterns = [
        (r"\bthere are\b", "list the items directly"),
        (r"\bthere is\b", "state directly"),
        (r"\bit is important to\b", "you should" or "must"),
        (r"\bit is possible to\b", "you can"),
        (r"\bit is necessary to\b", "you must"),
        (r"\bhave the ability to\b", "can"),
        (r"\bhave the option to\b", "can"),
        (r"\bare able to\b", "can")
    ]
    
    for pattern, suggestion in weak_verb_patterns:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            found_text = match.group()
            # Find the sentence containing this pattern
            containing_sentence = ""
            for sent in doc.sents:
                if found_text.lower() in sent.text.lower():
                    containing_sentence = sent.text.strip()
                    break
            
            suggestions.append(f"Issue: Weak verb construction detected - consider replacing '{found_text}' with '{suggestion}' for more direct communication")

    # 4. Highlight ambiguous words (e.g., 'file', 'mark', 'post', 'record', 'report')
#    ambiguous_words = r"\b(file|post|mark|screen|record|report)\b"
#    matches = re.finditer(ambiguous_words, text_content, flags=re.IGNORECASE)
#    for match in matches:
#       found_text = match.group()
#        suggestions.append(f"The word '{found_text}' can be ambiguous. Ensure the context clarifies its meaning.")

    return suggestions if suggestions else []