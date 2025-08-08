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
    # Only apply capitalization when words are used as nouns (key names), not as verbs
    key_terms = ['Ctrl', 'Shift', 'Esc', 'Enter', 'Tab', 'Spacebar', 'Delete', 'Backspace', 'Caps Lock', 'Num Lock', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
    
    # Create a mapping of key terms to their lowercase versions for verb checking
    verb_forms = {
        'Enter': 'enter',
        'Delete': 'delete', 
        'Shift': 'shift',
        'Tab': 'tab',
        'Esc': 'escape'  # 'esc' is not commonly used as a verb, but 'escape' is
    }
    
    for key in key_terms:
        pattern = rf'\b{key.lower()}\b'
        matches = re.finditer(pattern, content)
        for match in matches:
            if match.group() != key:
                # Get the word and its context for POS analysis
                word_start = match.start()
                word_end = match.end()
                
                # Find the sentence containing this word using spaCy
                word_found = False
                for sentence in doc.sents:
                    sentence_start = sentence.start_char
                    sentence_end = sentence.end_char
                    
                    if sentence_start <= word_start < sentence_end:
                        # Found the sentence containing our word
                        word_found = True
                        
                        # Find the token corresponding to our matched word
                        for token in sentence:
                            if (token.idx <= word_start < token.idx + len(token.text) or 
                                token.text.lower() == match.group().lower()):
                                
                                # Check if this token is used as a verb
                                is_verb = token.pos_ == "VERB"
                                
                                # Additional context checks for specific words
                                if key in verb_forms:
                                    verb_form = verb_forms[key]
                                    
                                    # Special handling for 'enter' - check for verb patterns
                                    if key == 'Enter' and token.text.lower() == 'enter':
                                        # Check if followed by objects (enter the room, enter data, etc.)
                                        next_tokens = [t for t in sentence[token.i+1:token.i+3]]
                                        has_object = any(t.pos_ in ["DET", "NOUN", "PRON"] for t in next_tokens)
                                        if is_verb or has_object:
                                            word_found = True
                                            break  # Skip capitalization - it's used as a verb
                                    
                                    # Special handling for 'delete' - check for verb patterns  
                                    elif key == 'Delete' and token.text.lower() == 'delete':
                                        # Check if it's used as a verb (delete the file, delete it, etc.)
                                        next_tokens = [t for t in sentence[token.i+1:token.i+3]]
                                        has_object = any(t.pos_ in ["DET", "NOUN", "PRON"] for t in next_tokens)
                                        if is_verb or has_object:
                                            word_found = True
                                            break  # Skip capitalization - it's used as a verb
                                    
                                    # Special handling for 'shift' - check for verb patterns
                                    elif key == 'Shift' and token.text.lower() == 'shift':
                                        # Check if it's used as a verb (shift the focus, shift to, etc.)
                                        if is_verb:
                                            word_found = True
                                            break  # Skip capitalization - it's used as a verb
                                    
                                    # Special handling for 'tab' - check for verb patterns
                                    elif key == 'Tab' and token.text.lower() == 'tab':
                                        # Check if it's used as a verb (tab through, tab to, etc.)
                                        if is_verb:
                                            word_found = True
                                            break  # Skip capitalization - it's used as a verb
                                
                                # If we reach here, it's likely used as a noun (key name)
                                suggestions.append(f"Capitalize key names: '{key}' (when referring to the key, not the action).")
                                word_found = True
                                break
                        
                        if word_found:
                            break
                
                # If we couldn't analyze with spaCy, fall back to simple pattern matching
                if not word_found:
                    # Basic verb pattern detection for fallback
                    if key == 'Enter' and re.search(r'\benter\s+(the|a|an|your|some|data|information|text)', content[match.start():match.end()+50], flags=re.IGNORECASE):
                        continue  # Skip - likely used as verb
                    elif key == 'Delete' and re.search(r'\bdelete\s+(the|a|an|this|that|files?|items?)', content[match.start():match.end()+50], flags=re.IGNORECASE):
                        continue  # Skip - likely used as verb
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