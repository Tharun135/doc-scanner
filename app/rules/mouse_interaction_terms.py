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
    
    # Rule 1: Use 'point to' instead of 'hover over' or 'mouse over'
    hover_terms = ['hover over', 'mouse over', 'hover']
    for term in hover_terms:
        pattern = rf'\b{term}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use 'point to' instead of '{match.group()}'.")

    # Rule 2: Use 'drag' and 'drop' appropriately
    # Ensure 'drag and drop' is used correctly
    drag_drop_pattern = r'\bdrag\s+and\s+drop\b'
    matches = re.finditer(drag_drop_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # No action needed; 'drag and drop' is acceptable
        pass

    # Check for incorrect usage of 'drag' and 'drop'
    drag_matches = re.finditer(r'\bdrag\b', content, flags=re.IGNORECASE)
    for match in drag_matches:
        # Ensure 'drag' is used correctly (e.g., not 'drag the mouse')
        context = content[max(0, match.start()-10):match.end()+10].lower()
        if 'mouse' in context:
            suggestions.append(f"Use 'drag' without mentioning the mouse, e.g., 'drag the item'.")

    drop_matches = re.finditer(r'\bdrop\b', content, flags=re.IGNORECASE)
    for match in drop_matches:
        # Ensure 'drop' is used correctly
        # Generally acceptable; no action needed unless misused
        pass

    # Rule 3: Use 'right-click' and 'double-click' with a hyphen
    click_terms = {'right click': 'right-click', 'double click': 'double-click'}
    for incorrect, correct in click_terms.items():
        pattern = rf'\b{incorrect}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use '{correct}' with a hyphen instead of '{match.group()}'.")

    # Rule 4: Avoid unnecessary mentions of the mouse
    mouse_phrases = [r'\bwith\s+the\s+mouse\b', r'\busing\s+the\s+mouse\b']
    for pattern in mouse_phrases:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid mentioning the mouse unless necessary. Remove '{match.group()}'.")

    # Rule 5: Be inclusive of different input methods
    # Avoid phrases like 'click with your mouse' or 'mouse over'
    inclusive_terms = [r'\bclick\s+with\s+your\s+mouse\b', r'\bmouse\s+over\b']
    for pattern in inclusive_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append("Use inclusive language that accommodates different input methods.")

    # Rule 6: Avoid anthropomorphizing the mouse
    # Phrases like 'the mouse wants you to...'
    anthropomorphic_patterns = [r'\bmouse\s+(\w+\s+){0,3}(want|needs|asks)\b']
    for pattern in anthropomorphic_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Avoid anthropomorphizing the mouse. Rephrase '{match.group()}'.")

    # Rule 7: Use 'scroll' appropriately
    scroll_matches = re.finditer(r'\bscroll\b', content, flags=re.IGNORECASE)
    for match in scroll_matches:
        # Ensure 'scroll' is used to refer to moving content, not the mouse wheel
        context = content[max(0, match.start()-20):match.end()+20].lower()
        if 'mouse' in context and 'wheel' in context:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'scroll' to refer to moving content, not the mouse wheel.")

    # Rule 8: Use 'press and hold' instead of 'click and hold'
    click_hold_pattern = r'\bclick\s+and\s+hold\b'
    matches = re.finditer(click_hold_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'press and hold' instead of 'click and hold'.")

    return suggestions if suggestions else []
