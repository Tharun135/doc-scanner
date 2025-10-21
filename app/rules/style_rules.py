import re
import spacy
from bs4 import BeautifulSoup

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

# Load spaCy model lazily to avoid startup issues
nlp = None

def _get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
        nlp.max_length = 3000000  # Increase max length to 3MB
    return nlp

def check(content):
    suggestions = []

    # Extract plain text (remove HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    try:
        nlp_model = _get_nlp()
        doc = nlp_model(text_content)
    except Exception as e:
        doc = None

    # ------------------------------
    # Regex-based style checks
    # ------------------------------
    # Check for passive voice using "by" + past participle
    if re.search(r"\bby\s+\w+ed\b", text_content, flags=re.IGNORECASE):
        suggestions.append("Consider avoiding passive voice where possible.")

    # Multiple exclamation marks check removed per user request
    # if re.search(r"!{2,}", text_content):
    #     suggestions.append("Avoid using multiple exclamation marks.")

    # ALL CAPS check removed per user request

    # ------------------------------
    # spaCy-based style checks
    # ------------------------------
    if doc is not None:
        for sent in doc.sents:
            # Skip titles and headings for style checks
            if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
                continue
                
            # Example 2: Adverbs ending with -ly (may weaken writing)
            for token in sent:
                if token.text.endswith("ly") and token.pos_ == "ADV":
                    suggestions.append(f"Check use of adverb: '{token.text}' in sentence '{sent.text.strip()}'")

            # Example 3: Detecting overuse of 'very'
            if "very" in sent.text.lower():
                suggestions.append(f"Try replacing or removing 'very': '{sent.text.strip()}'")

    # ------------------------------
    # RAG-based contextual style checks (if available)
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="style")
        suggestions.extend(rag_suggestions)

    return suggestions
