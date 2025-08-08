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

# Load spaCy English model
nlp = get_nlp_model()

def check(content):
    """Check for manual steps and action verb improvements."""
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content, 
            "manual_steps_rewriting",
            "Check for opportunities to convert procedural text into clear, numbered manual steps with imperative verbs."
        )
        if rag_suggestions:
            return rag_suggestions
    
    doc = nlp(text_content)
    
    # Rule 1: Check for verb forms that could be converted to imperative
    action_verbs = {
        r'\bclicks?\b': 'Click',
        r'\bselects?\b': 'Select', 
        r'\bopens?\b': 'Open',
        r'\btypes?\b': 'Enter',
        r'\bputs?\b': 'Enter',
        r'\bscrolls?\b': 'Scroll',
        r'\bexpands?\b': 'Expand',
        r'\bloads?\b': 'Load',
        r'\bnavigates?(?!\s+to)\b': 'Navigate to',  # Only match "navigate(s)" not followed by "to"
        r'\bdrags?\b': 'Drag',
        r'\bdrops?\b': 'Drop',
        r'\bhighlights?\b': 'Highlight',
        r'\bchooses?\b': 'Choose',
        r'\bpresses?\b': 'Press'
    }
    
    for pattern, replacement in action_verbs.items():
        if re.search(pattern, text_content, re.IGNORECASE):
            # Check if it's in a procedural context
            sentences_with_action = []
            for sent in doc.sents:
                if re.search(pattern, sent.text, re.IGNORECASE):
                    sentences_with_action.append(sent.text.strip())
            
            if sentences_with_action and _is_procedural_context(sentences_with_action):
                # Find the specific sentence with the verb
                for sent in doc.sents:
                    sent_verb_match = re.search(pattern, sent.text, re.IGNORECASE)
                    if sent_verb_match:
                        found_verb = sent_verb_match.group()
                        
                        # Special handling for "types" - check if it's used as a verb or noun
                        if pattern == r'\btypes?\b':
                            if not _is_types_verb_usage(sent, found_verb):
                                continue  # Skip if "types" is used as a noun
                        
                        # Special handling for "navigate" - skip if already followed by "to"
                        if pattern == r'\bnavigates?(?!\s+to)\b':
                            # Double-check that "to" doesn't immediately follow in the sentence
                            match_end = sent_verb_match.end()
                            remaining_text = sent.text[match_end:].lstrip()
                            if remaining_text.lower().startswith('to'):
                                continue  # Skip if "to" follows the matched verb
                        
                        # Only suggest if the found verb is different from the replacement
                        if found_verb.lower() != replacement.lower():
                            suggestions.append({
                                "text": sent.text.strip(),
                                "start": sent.start_char,
                                "end": sent.end_char,
                                "message": f"Consider using imperative form '{replacement}' instead of '{found_verb}' for clearer instructions."
                            })
                        break  # Only add suggestion once per pattern
    
    # Rule 2: Check for sequences that could be numbered steps
    if _has_sequential_indicators(text_content):
        suggestions.append({
            "text": text_content[:100] + "..." if len(text_content) > 100 else text_content,
            "start": 0,
            "end": len(text_content),
            "message": "This content appears to contain sequential instructions. Consider formatting as numbered manual steps."
        })
    
    return suggestions

def _is_procedural_context(sentences):
    """Check if sentences are in a procedural/instructional context."""
    procedural_indicators = [
        'to', 'in order to', 'navigate', 'menu', 'button', 'field', 'dialog',
        'window', 'tab', 'panel', 'option', 'setting', 'configuration',
        'application', 'app', 'software', 'program', 'tool', 'interface',
        'screen', 'page', 'form', 'dropdown', 'checkbox', 'textbox',
        'link', 'icon', 'toolbar', 'sidebar', 'header', 'footer'
    ]
    
    # Additional indicators for user actions
    action_indicators = [
        'user', 'operator', 'technician', 'person', 'you', 'they',
        'click', 'select', 'open', 'close', 'press', 'enter', 'type', 'types',
        'scroll', 'drag', 'drop', 'choose', 'navigate'
    ]
    
    combined_text = ' '.join(sentences).lower()
    
    # Check for procedural indicators
    has_procedural = any(indicator in combined_text for indicator in procedural_indicators)
    
    # Check for action indicators (user performing actions)
    has_actions = any(indicator in combined_text for indicator in action_indicators)
    
    # If it has either type of indicator, consider it procedural
    return has_procedural or has_actions

def _has_sequential_indicators(text):
    """Check for words that indicate sequential steps."""
    sequential_words = [
        'first', 'second', 'third', 'then', 'next', 'after', 'finally',
        'subsequently', 'following', 'afterward', 'step'
    ]
    
    text_lower = text.lower()
    return sum(1 for word in sequential_words if word in text_lower) >= 2

def _is_types_verb_usage(sentence, found_verb):
    """Check if 'types' is being used as a verb (for input action) rather than a noun."""
    # Parse the sentence to get tokens
    doc = nlp(sentence.text)
    
    for token in doc:
        if token.text.lower() == found_verb.lower():
            # First check for clear noun usage patterns that should be excluded
            # If it's followed by "of", it's definitely a noun (types of X)
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.text.lower() == "of":
                return False  # This is "types of X", not a typing action
            
            # Check for adjective + types patterns (different types, various types, etc.)
            prev_token = token.nbor(-1) if token.i > 0 else None
            if prev_token and prev_token.text.lower() in ['different', 'various', 'several', 'multiple', 'many', 'two', 'three', 'all']:
                return False  # This is describing categories/kinds
            
            # If "types" is at the beginning and followed by "of", it's a noun
            if token.i == 0 and next_token and next_token.text.lower() == "of":
                return False
            
            # Now check for verb usage patterns
            sentence_text = sentence.text.lower()
            
            # Strong indicators of typing action - if any of these are present, it's likely a verb
            typing_indicators = [
                'password', 'username', 'text', 'data', 'value', 'name', 'field', 'box',
                'form', 'dialog', 'input', 'characters', 'letters', 'numbers', 'code',
                'information', 'details', 'into', 'in the', 'into the', 'keyboard',
                'key', 'enter', 'character'
            ]
            
            # Strong indicators of an actor performing the action
            actor_indicators = ['user', 'operator', 'technician', 'person', 'you', 'they', 'he', 'she']
            
            # Check for typing context
            has_typing_context = any(indicator in sentence_text for indicator in typing_indicators)
            has_actor = any(actor in sentence_text for actor in actor_indicators)
            
            # If we have both an actor and typing context, it's definitely a verb
            if has_actor and has_typing_context:
                return True
            
            # If we have strong typing context, even without explicit actor, it's likely a verb
            if has_typing_context:
                return True
            
            # If there's an actor and the word after "types" is not "of" or auxiliary verbs, it's likely a verb
            if has_actor:
                if next_token and next_token.text.lower() not in ['of', 'are', 'is', 'can', 'will', 'were', 'was']:
                    return True
            
            # Check if the POS tag suggests it's a verb
            if token.pos_ == "VERB":
                return True
    
    return False  # Default to not a verb usage if we can't determine

def convert_to_manual_steps(text):
    """Legacy function for converting text to manual steps format."""
    soup = BeautifulSoup(text, "html.parser")
    clean_text = html.unescape(soup.get_text())

    doc = nlp(clean_text)
    steps = []

    for i, sent in enumerate(doc.sents, 1):
        sent_text = sent.text.strip()

        # Simple present conversion patterns
        sent_text = re.sub(r"\bclicks?\b", "Click", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bselects?\b", "Select", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bopens?\b", "Open", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\btypes?\b", "Enter", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bputs?\b", "Enter", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bscrolls?\b", "Scroll", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bexpands?\b", "Expand", sent_text, flags=re.IGNORECASE)
        sent_text = re.sub(r"\bloads?\b", "Load", sent_text, flags=re.IGNORECASE)

        # Highlight common UI terms
        sent_text = re.sub(r"(OPC UA Server|Server URL|Connect|Namespace|Add/Import|Next Step|Tags|Model|Security Policy|Authentication Type|HMI_RT_1|HMIRuntime)", r"**\1**", sent_text)

        # Capitalize first letter
        if sent_text:
            sent_text = sent_text[0].upper() + sent_text[1:]

        # Ensure it ends in a period
        if not sent_text.endswith("."):
            sent_text += "."

        steps.append(f"{i}. {sent_text}")

    return steps
