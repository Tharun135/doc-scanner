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

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Extract plain text (remove HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # ------------------------------
    # Regex-based style checks
    # ------------------------------
    # Check for passive voice using "by" + past participle
    if re.search(r"\bby\s+\w+ed\b", text_content, flags=re.IGNORECASE):
        suggestions.append("Consider avoiding passive voice where possible.")

    # Multiple exclamation marks check removed per user request
    # if re.search(r"!{2,}", text_content):
    #     suggestions.append("Avoid using multiple exclamation marks.")

    # Check for all-caps words (likely shouting) - skip markdown info blocks
    caps_matches = re.finditer(r"\b[A-Z]{5,}\b", text_content)
    for match in caps_matches:
        # Skip ALL CAPS words that are inside markdown info/note quotes
        context_start = max(0, match.start() - 20)
        context_end = min(len(text_content), match.end() + 20)
        context = text_content[context_start:context_end]
        
        # Skip if it's part of markdown info syntax like: info "NOTICE"
        if re.search(r'(info|warning|note|tip|caution)\s*"[^"]*' + re.escape(match.group()) + r'[^"]*"', context, re.IGNORECASE):
            continue
            
        # Skip if the CAPS word is in a title or heading
        caps_word = match.group()
        if TITLE_UTILS_AVAILABLE:
            # Find which sentence contains this caps word
            caps_position = match.start()
            for sent in doc.sents:
                sent_start = sent.start_char
                sent_end = sent.end_char
                if sent_start <= caps_position < sent_end:
                    if is_title_or_heading(sent.text.strip(), content):
                        break  # Skip this caps word as it's in a title
            else:
                # Not in a title, so add suggestion
                suggestions.append("Avoid using ALL CAPS for emphasis. Use bold or italics instead.")
                break  # Only report once per document
        else:
            # If title utils not available, add suggestion
            suggestions.append("Avoid using ALL CAPS for emphasis. Use bold or italics instead.")
            break  # Only report once per document

    # ------------------------------
    # spaCy-based style checks
    # ------------------------------
    for sent in doc.sents:
        # Skip titles and headings for style checks
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
            continue
            
        # Example 1: Long, wordy sentences
        if len(sent.text.split()) > 25:
            suggestions.append(f"Consider simplifying this sentence: '{sent.text.strip()}'")

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
