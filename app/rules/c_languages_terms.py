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

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Ensure correct usage of 'C', 'C++', and 'C#'
    
    # Check for incorrect "C/C++" or "C/C++/C#" usage
    c_cpp_pattern = r'\bC/C\+\+/?C#?\b'
    matches = re.finditer(c_cpp_pattern, content)
    for match in matches:
        suggestions.append("Avoid using 'C/C++' or 'C/C++/C#'; refer to each language separately (e.g., 'C, C++, and C#').")

    # Check for "C-Sharp" (incorrect formatting for C#)
    csharp_pattern = r'\bC[-\s]?sharp\b'
    matches = re.finditer(csharp_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Use 'C#' instead of '{match.group()}' when referring to the programming language.")

    # Check for lowercase 'c', 'c++', or 'c#'
    lowercase_c_patterns = {
        'c': r'\bc\b',
        'c++': r'\bc\+\+\b',
        'c#': r'\bc#\b',
    }
    
    for language, pattern in lowercase_c_patterns.items():
        matches = re.finditer(pattern, content)
        for match in matches:
            suggestions.append("Capitalize '{match.group()}' to '{language.upper()}'.")
    
    return suggestions if suggestions else []
