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
    # Rule 1: Check for unnecessary use of "can"
    for token in doc:
        if token.text.lower() == "can" and token.dep_ == "aux":
            sentence = token.sent.text
            # Suggest rephrasing if possible
            suggestions.append("Consider rewriting to describe the action instead of using 'can'.")
    
    # Rule 2: Check for proper use of "may" and suggest replacing it with "might"
    may_pattern = r'\bmay\b'
    matches = re.finditer(may_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append("Avoid using 'may' as it can imply permission. Consider using 'might' to express possibility.")

    # Rule 3: Ensure "could" is used only for the past and not as a substitute for "can"
    could_pattern = r'\bcould\b'
    matches = re.finditer(could_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 30
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end]
        if "past" not in context.lower():
            suggestions.append("Ensure 'could' is only used to describe the past. Use 'can' for present actions.")

    # Rule: Detect overuse of "can" and suggest rewording
    can_count = len([token for token in doc if token.text.lower() == "can"])
    if can_count > 3:  # Threshold for overuse (customizable)
        suggestions.append("Consider rephrasing to avoid overusing 'can'.")


    # Rule: Detect "can" being used to express permission
    for token in doc:
        if token.text.lower() == "can" and "permission" in token.sent.text.lower():
            suggestions.append("Avoid using 'can' to express permission. Consider using 'allowed to' or 'able to'.")

    return suggestions if suggestions else []