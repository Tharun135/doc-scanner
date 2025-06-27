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
    # Rule 1: Use "run" instead of "carry out" for commands, macros, and programs
    carry_out_pattern = r'\b(carry\s+out)\b'
    matches = re.finditer(carry_out_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'run' instead of 'carry out' for actions related to commands, macros, and programs.")

    # Rule 2: Use "run" instead of "execute" for commands, macros, and programs
    execute_pattern = r'\b(execute)\b'
    matches = re.finditer(execute_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'run' instead of 'execute' when referring to commands, macros, or programs. 'Execute' can be used in specific contexts but generally, 'run' is preferred.")

    # Rule: Detect overuse of "execute" and suggest using "run"
    execute_count = len([token for token in doc if token.text.lower() == "execute"])
    if execute_count > 3:  # Threshold for overuse (customizable)
        suggestions.append("Consider using 'run' instead of 'execute' to describe actions related to commands or programs.")


    # Rule: Ensure "carry out" is used only in non-technical contexts
    for token in doc:
        if token.text.lower() == "carry" and token.head.text.lower() == "out":
            context_window = 30  # Check surrounding words
            start = max(0, token.idx - context_window)
            end = min(len(content), token.idx + context_window)
            context = content[start:end]
            if "command" in context.lower() or "macro" in context.lower() or "program" in context.lower():
#                line_number = get_line_number(content, token.idx)
                suggestions.append("Use 'run' instead of 'carry out' in technical contexts like commands, macros, or programs.")

    # Rule: Suggest using "run" for simple commands instead of "execute"
    for token in doc:
        if token.text.lower() == "execute" and token.head.text.lower() == "command":
#            line_number = get_line_number(content, token.idx)
            suggestions.append("Use 'run' instead of 'execute' for simpler commands.")
    return suggestions if suggestions else []