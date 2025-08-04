"""
Rule for detecting redundant phrases and unnecessary verbosity.
Helps improve conciseness by identifying and suggesting removal of redundant expressions.
"""

import re
from bs4 import BeautifulSoup
import html
from .spacy_utils import get_nlp_model, process_text

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

def check(content):
    """Check for redundant phrases and unnecessary verbosity."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "redundant_phrases",
            "Detect redundant phrases, unnecessary verbosity, and suggest more concise alternatives."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    doc = process_text(text_content)

    # Rule 1: Redundant prepositional phrases
    redundant_phrases = {
        r'\bin the process of\b': 'while',
        r'\bfor the purpose of\b': 'to',
        r'\bin the event that\b': 'if',
        r'\bdue to the fact that\b': 'because',
        r'\bby means of\b': 'by',
        r'\bwith regard to\b': 'about',
        r'\bin relation to\b': 'about',
        r'\bwith respect to\b': 'about',
        r'\bin connection with\b': 'about',
        r'\bat the present time\b': 'now',
        r'\bat this point in time\b': 'now',
        r'\bin the near future\b': 'soon',
        r'\bin the immediate vicinity\b': 'near',
        r'\bat the location of\b': 'at',
    }

    for pattern, replacement in redundant_phrases.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            suggestions.append(f"Redundant phrase: Replace '{phrase}' with '{replacement}' for conciseness.")

    # Rule 2: Redundant adjectives and modifiers
    redundant_modifiers = [
        r'\bcompletely eliminate\b',  # eliminate already means completely remove
        r'\btotally destroy\b',       # destroy already means completely
        r'\bexactly identical\b',     # identical means exactly the same
        r'\bvery unique\b',           # unique cannot be qualified
        r'\bmost optimal\b',          # optimal is already the best
        r'\bend result\b',            # result implies end
        r'\bfinal outcome\b',         # outcome implies final
        r'\bfuture plans\b',          # plans are for the future
        r'\bpast history\b',          # history is always past
        r'\bunexpected surprise\b',   # surprises are unexpected
        r'\badvance warning\b',       # warnings are advance notice
    ]

    for pattern in redundant_modifiers:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            base_word = phrase.split()[-1]  # Get the last word as the base
            suggestions.append(f"Redundant modifier: '{phrase}' - consider using just '{base_word}'.")

    # Rule 3: Wordy expressions with simple alternatives
    wordy_expressions = {
        r'\ba large number of\b': 'many',
        r'\ba small number of\b': 'few',
        r'\bin spite of the fact that\b': 'although',
        r'\bowing to the fact that\b': 'because',
        r'\bas a result of\b': 'because of',
        r'\bin order to\b': 'to',
        r'\bfor the reason that\b': 'because',
        r'\bhas the ability to\b': 'can',
        r'\bis able to\b': 'can',
        r'\bprior to\b': 'before',
        r'\bsubsequent to\b': 'after',
        r'\bduring the course of\b': 'during',
        r'\bat the time when\b': 'when',
        r'\bin the course of\b': 'during',
    }

    for pattern, replacement in wordy_expressions.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            suggestions.append(f"Wordy expression: Replace '{phrase}' with '{replacement}'.")

    # Rule 4: Double negatives and complex constructions
    complex_constructions = [
        r'\bnot un\w+',               # not uncommon -> common
        r'\bnot in\w+',               # not infrequent -> frequent
        r'\bis not without\b',        # is not without -> has
        r'\bcannot help but\b',       # cannot help but -> must
        r'\bcan\'t help but\b',       # can't help but -> must
    ]

    for pattern in complex_constructions:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            suggestions.append(f"Complex construction: Simplify '{phrase}' for clarity.")

    # Rule 5: Unnecessary intensifiers
    unnecessary_intensifiers = [
        r'\bvery\s+\w+',
        r'\bquite\s+\w+',
        r'\brather\s+\w+',
        r'\bextremely\s+\w+',
        r'\bhighly\s+\w+',
        r'\btruly\s+\w+',
        r'\breally\s+\w+',
    ]

    for pattern in unnecessary_intensifiers:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            base_word = phrase.split()[-1]
            suggestions.append(f"Unnecessary intensifier: Consider removing '{phrase.split()[0]}' from '{phrase}' or use a stronger word than '{base_word}'.")

    return suggestions if suggestions else []
