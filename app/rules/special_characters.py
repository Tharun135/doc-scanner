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
    
    # Rule 1: Use 'and' instead of '&' unless part of a formal name
    ampersand_pattern = r'&'
    matches = re.finditer(ampersand_pattern, text_content)
    for match in matches:
        suggestions.append("Use 'and' instead of '&' unless it's part of a formal name.")
    
    # Rule 2: Proper use of ellipsis
    ellipsis_pattern = r'\.{3,}'
    matches = re.finditer(ellipsis_pattern, text_content)
    for match in matches:
        suggestions.append(f"Use an ellipsis (…) character instead of '{match.group()}'.")
    
    # Rule 3: Correct use of quotation marks
    # Ensure double quotation marks are used for UI string references
    # Exception: Single quotes can be used for admonitions like NOTICE, WARNING, CAUTION, and DANGER
    single_quote_pattern = r"'[^']*'"
    matches = re.finditer(single_quote_pattern, text_content)
    for match in matches:
        matched_text = match.group()

        # Check if the matched text is an admonition
        admonitions = ["NOTICE", "WARNING", "CAUTION", "DANGER"]
        if any(admonition in matched_text.upper() for admonition in admonitions):
            continue

        suggestions.append("Use double quotation marks for UI string references instead of single quotes.")
    
    # Rule 4: Avoid using apostrophes for plurals
    apostrophe_plural_pattern = r"\b\w+'s\b"
    matches = re.finditer(apostrophe_plural_pattern, text_content)
    for match in matches:
        word = match.group()
        if not word.lower() in ["it's", "he's", "she's", "who's", "that's", "let's"]:
            suggestions.append(f"Do not use an apostrophe to form plurals: '{word}'.")

    # Rule 5: Avoid nesting parentheses
    nested_parentheses_pattern = r'\([^\(\)]*\([^\(\)]*\)[^\(\)]*\)'
    matches = re.finditer(nested_parentheses_pattern, text_content)
    for match in matches:
        suggestions.append("Avoid nesting parentheses; consider rephrasing.")
    
    # Rule 6: Avoid using symbols in place of words
    symbol_substitutions = {
        '@': 'at',
        '#': 'number',
        '%': 'percent',
        '+': 'plus',
        '=': 'equals',
        '<': 'less than',
        '>': 'greater than'
    }
    for symbol, word in symbol_substitutions.items():
        pattern = rf'\b\w*{re.escape(symbol)}\w*\b'
        matches = re.finditer(pattern, text_content)
        for match in matches:
            suggestions.append(f"Avoid using '{symbol}' in place of words; spell out the word '{word}'.")

    # Rule 7: Currency symbols placement
    currency_pattern = r'(\b\d+(\.\d{1,2})?\s*(\$|€|£|¥))'
    matches = re.finditer(currency_pattern, text_content)
    for match in matches:
        suggestions.append(f"Place the currency symbol before the amount, e.g., '{match.group(1)}' should be formatted as '{match.group(1)}'.")
    
    # Rule 8: Identify and evaluate tables separately
    table_pattern = r'^\|.*\|\s*\n(\|[-:]+\|)+'
    matches = re.finditer(table_pattern, text_content, re.MULTILINE)
    for match in matches:
        suggestions.append("Table detected. Evaluate it separately.")

    return suggestions if suggestions else []