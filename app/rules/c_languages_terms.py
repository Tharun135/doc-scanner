import re
import spacy
from bs4 import BeautifulSoup
import html

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

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
