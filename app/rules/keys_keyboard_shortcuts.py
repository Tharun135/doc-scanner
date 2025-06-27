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
    
    # Rule 1: Use '+' to indicate simultaneous key presses (e.g., 'Ctrl+C')
    keyboard_shortcut_patterns = [
        r'\bCtrl\+\s?(\w)\b',      # e.g., 'Ctrl+ C'
        r'\bCtrl\s?-\s?(\w)\b',    # e.g., 'Ctrl-C'
        r'\bCtrl\s(\w)\b',         # e.g., 'Ctrl C' (missing '+')
        r'\bCtrl\+\+\s?(\w)\b'     # e.g., 'Ctrl++C'
    ]
    for pattern in keyboard_shortcut_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Ensure keyboard shortcuts are formatted correctly using '+'. For example, 'Ctrl+{match.group(1).upper()}'.")
    
    # Rule 2: Use 'then' to indicate sequential key presses (e.g., 'Alt+F, then S')
    sequential_shortcut_patterns = [
        r'\b(Alt|Ctrl|Shift)\+(\w),?\s*(\w)\b'  # e.g., 'Alt+F S'
    ]
    for pattern in sequential_shortcut_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            suggestions.append(f"Use 'then' to indicate sequential key presses. For example, '{match.group(1)}+{match.group(2)}, then {match.group(3)}'.")
    
    # Rule 3: Use specific key names and capitalization
    key_names = {
        'escape': 'Esc',
        'return': 'Enter',
        'delete': 'Delete',
        'backspace': 'Backspace',
        'tab': 'Tab',
        'spacebar': 'Spacebar',
        'windows key': 'Windows logo key',
        'arrow keys': 'Arrow keys',
        'left arrow': 'Left Arrow key',
        'right arrow': 'Right Arrow key',
        'up arrow': 'Up Arrow key',
        'down arrow': 'Down Arrow key'
    }
    for incorrect, correct in key_names.items():
        pattern = rf'\b{incorrect}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            if match.group().lower() != correct.lower():
                suggestions.append(f"Use '{correct}' instead of '{match.group()}'. Ensure correct capitalization.")
    
    # Rule 4: Capitalize key names and avoid unnecessary words like 'button' or 'key'
    key_terms = ['Ctrl', 'Shift', 'Esc', 'Enter', 'Tab', 'Spacebar', 'Delete', 'Backspace', 'Caps Lock', 'Num Lock', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
    for key in key_terms:
        pattern = rf'\b{key.lower()}\b'
        matches = re.finditer(pattern, content)
        for match in matches:
            if match.group() != key:
                # Check if 'enter' is used as a verb
                if key == 'Enter' and re.search(r'\benter\b', match.group(), flags=re.IGNORECASE):
                    # Check if 'enter' is used as a verb
                    if re.search(r'\benter\b\s+(the|a|an|your|some|any|my|their|his|her|its|our)\s+\w+', match.group(), flags=re.IGNORECASE):
                        continue  # Skip suggesting capitalization if 'enter' is used as a verb
                    else:
                        suggestions.append(f"Capitalize key names: '{key}'.")
                else:
                    suggestions.append(f"Capitalize key names: '{key}'.")
        # Avoid unnecessary words like 'key' or 'button' after key names
        unnecessary_terms_pattern = rf'\b{key}\s+(key|button)\b'
        matches = re.finditer(unnecessary_terms_pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid unnecessary words like '{match.group(1)}' after key names.")
    
    # Rule 5: Use 'select' instead of 'choose' or 'pick' for UI actions
    alternative_verbs = ['choose', 'pick']
    for verb in alternative_verbs:
        pattern = rf'\b{verb}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use 'select' instead of '{match.group()}' for UI actions.")
    
    # Rule 6: Use consistent terminology for pointing devices (e.g., 'mouse pointer' not 'cursor')
    cursor_matches = re.finditer(r'\bcursor\b', content, flags=re.IGNORECASE)
    for match in cursor_matches:
        suggestions.append("Use 'mouse pointer' instead of 'cursor' when referring to pointing devices.")
    
    # Rule 7: Use 'press' for keys and 'select' for UI elements
    press_select_patterns = [
        (r'\bpress\b.*\b(button|option|menu|link)\b', "Use 'select' instead of 'press' when referring to UI elements."),
        (r'\bclick\b.*\b(key|shortcut)\b', "Use 'press' instead of 'click' when referring to keys.")
    ]
    for pattern, suggestion_text in press_select_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            # Ensure the context is correct before suggesting
            if 'key' in match.group() or 'shortcut' in match.group():
                suggestions.append(suggestion_text)
            elif 'button' in match.group() or 'option' in match.group() or 'menu' in match.group() or 'link' in match.group():
                suggestions.append("Use 'select' instead of 'press' when referring to UI elements.")
    
    # Rule 8: Use 'right-click' and 'double-click' appropriately
    incorrect_click_patterns = [
        (r'\bright click\b', "Use 'right-click' with a hyphen."),
        (r'\bdouble click\b', "Use 'double-click' with a hyphen.")
    ]
    for pattern, suggestion_text in incorrect_click_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(suggestion_text)
    
    # Rule 9: Avoid using 'hit' or 'tap' for key presses; use 'press'
    verbs_to_avoid = ['hit', 'tap']
    for verb in verbs_to_avoid:
        pattern = rf'\b{verb}\b.*\b(key|keys)\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use 'press' instead of '{verb}' when referring to key presses.")
    
    return suggestions if suggestions else []