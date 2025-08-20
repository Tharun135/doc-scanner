import spacy
import textstat
from bs4 import BeautifulSoup

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Thresholds (can be tuned per project)
SENTENCE_LENGTH_THRESHOLD = 25   # words
FLESCH_READING_EASE_THRESHOLD = 60  # 0–100 scale, higher = easier
GRADE_LEVEL_THRESHOLD = 12       # typical max grade level for manuals

def check(content):
    suggestions = []

    # Extract plain text (strip HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)

    # ------------------------------
    # Sentence length checks
    # ------------------------------
    for sent in doc.sents:
        word_count = len([t for t in sent if t.is_alpha])
        if word_count > SENTENCE_LENGTH_THRESHOLD:
            suggestions.append(
                f"Sentence too long ({word_count} words). Consider breaking it up: '{sent.text.strip()}'"
            )

    # ------------------------------
    # Textstat readability checks
    # ------------------------------
    flesch = textstat.flesch_reading_ease(text_content)
    grade = textstat.flesch_kincaid_grade(text_content)

    if flesch < FLESCH_READING_EASE_THRESHOLD:
        suggestions.append(
            f"Low readability (Flesch score: {flesch}). Simplify language."
        )
    if grade > GRADE_LEVEL_THRESHOLD:
        suggestions.append(
            f"High grade level ({grade}). Aim for Grade {GRADE_LEVEL_THRESHOLD} or below."
        )

    # ------------------------------
    # Domain-specific readability checks via RAG
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="readability")
        suggestions.extend(rag_suggestions)

    return suggestions
