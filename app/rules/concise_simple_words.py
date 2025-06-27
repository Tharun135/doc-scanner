import re
import spacy
from bs4 import BeautifulSoup
import html

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
            if replacement:
                suggestions.append(f"Replace '{found_text}' with '{replacement}' for simplicity.")
            else:
                suggestions.append(f"Consider removing '{found_text}' as it may not add value.")

    # 2. Detect unnecessary adverbs
    unnecessary_adverbs = r"\b(very|quite|easily|effectively|quickly)\b"
    matches = re.finditer(unnecessary_adverbs, text_content, flags=re.IGNORECASE)
    for match in matches:
        found_text = match.group()
        suggestions.append(f"Consider removing the adverb '{found_text}' unless it is essential.")

    # 3. Flag weak or vague verbs
    weak_verbs = r"\b(be|have)\b"
    matches = re.finditer(weak_verbs, text_content, flags=re.IGNORECASE)
    for match in matches:
        found_text = match.group()
        suggestions.append(f"Avoid the weak verb '{found_text}'. Replace it with a more specific action verb.")

    # 4. Highlight ambiguous words (e.g., 'file', 'mark', 'post', 'record', 'report')
#    ambiguous_words = r"\b(file|post|mark|screen|record|report)\b"
#    matches = re.finditer(ambiguous_words, text_content, flags=re.IGNORECASE)
#    for match in matches:
#       found_text = match.group()
#        suggestions.append(f"The word '{found_text}' can be ambiguous. Ensure the context clarifies its meaning.")

    return suggestions if suggestions else []