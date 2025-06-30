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
        # Find the sentence containing the ampersand
        sentences = [sent.text.strip() for sent in doc.sents]
        containing_sentence = ""
        for sentence in sentences:
            if '&' in sentence:
                containing_sentence = sentence
                break
        suggestions.append(f"Issue: Use of '&' symbol instead of 'and'\nOriginal sentence: {containing_sentence}\nAI suggestion: Use 'and' instead of '&' unless it's part of a formal name.")
    
    # Rule 2: Proper use of ellipsis
    ellipsis_pattern = r'\.{3,}'
    matches = re.finditer(ellipsis_pattern, text_content)
    for match in matches:
        # Find the sentence containing the ellipsis
        sentences = [sent.text.strip() for sent in doc.sents]
        containing_sentence = ""
        for sentence in sentences:
            if match.group() in sentence:
                containing_sentence = sentence
                break
        suggestions.append(f"Issue: Incorrect ellipsis format\nOriginal sentence: {containing_sentence}\nAI suggestion: Use an ellipsis (…) character instead of '{match.group()}'.")
    
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
    
    # Rule 4: Check apostrophe usage - avoid for plurals, allow for possession
    # Important: Apostrophes are acceptable when indicating possession (the "of" relationship)
    # Examples: "Tharun's laptop" = "laptop of Tharun", "user's guide" = "guide of the user"
    # However, avoid apostrophes for plurals: use "APIs" not "API's", "databases" not "database's"
    # Note: spaCy tokenizes "word's" as two tokens: "word" and "'s"
    
    for sent in doc.sents:
        for i, token in enumerate(sent):
            if token.text == "'s" and token.pos_ == "PART":
                # Get the word before the 's
                if i > 0:
                    base_word_token = sent[i - 1]
                    full_word = base_word_token.text + "'s"
                    
                    # Skip common contractions
                    contractions = ["it's", "he's", "she's", "who's", "that's", "let's", "what's", "where's", "there's", "here's"]
                    if full_word.lower() in contractions:
                        continue
                    
                    # Get next token after 's
                    next_token = sent[i + 1] if i + 1 < len(sent) else None
                    
                    # Detect plural misuse patterns
                    is_likely_plural_misuse = False
                    
                    # Pattern 1: Subject + 's + verb (especially "are", "were", etc.)
                    if (base_word_token.dep_ == "nsubj" and 
                        next_token and next_token.pos_ in ["AUX", "VERB"] and
                        next_token.text.lower() in ["are", "were", "have", "will", "can", "should"]):
                        is_likely_plural_misuse = True
                    
                    # Pattern 2: Determiners indicating plural + word's + verb
                    prev_prev_token = sent[i - 2] if i > 1 else None
                    if (prev_prev_token and 
                        prev_prev_token.text.lower() in ["all", "many", "several", "these", "those", "some"] and
                        next_token and next_token.pos_ in ["AUX", "VERB"]):
                        is_likely_plural_misuse = True
                    
                    # Generate warning for likely plural misuse
                    if is_likely_plural_misuse:
                        base_word = base_word_token.text
                        sentence = sent.text.strip()
                        suggestions.append(f"Issue: Incorrect apostrophe usage for plural form\nOriginal sentence: {sentence}\nAI suggestion: Use '{base_word}s' instead of '{full_word}' for multiple items. Use apostrophes only for possession (e.g., 'Tharun's laptop' = 'laptop of Tharun').")

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