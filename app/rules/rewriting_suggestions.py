import re
import spacy
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
nlp = spacy.load("en_core_web_sm")

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
        r'\bnavigates?\b': 'Navigate to',
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
    
    # Rule 3: Check for missing step formatting in procedural text
    if _is_instruction_text(text_content) and not _has_step_formatting(text_content):
        suggestions.append({
            "text": text_content[:100] + "..." if len(text_content) > 100 else text_content,
            "start": 0,
            "end": len(text_content),
            "message": "This appears to be instructional content. Consider organizing as clear, numbered steps."
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
    
    combined_text = ' '.join(sentences).lower()
    return any(indicator in combined_text for indicator in procedural_indicators)

def _has_sequential_indicators(text):
    """Check for words that indicate sequential steps."""
    sequential_words = [
        'first', 'second', 'third', 'then', 'next', 'after', 'finally',
        'subsequently', 'following', 'afterward', 'step'
    ]
    
    text_lower = text.lower()
    return sum(1 for word in sequential_words if word in text_lower) >= 2

def _is_instruction_text(text):
    """Check if text appears to be instructional."""
    instruction_indicators = [
        'click', 'select', 'open', 'navigate', 'enter', 'choose', 'press',
        'go to', 'access', 'configure', 'set up', 'install', 'download'
    ]
    
    text_lower = text.lower()
    return sum(1 for indicator in instruction_indicators if indicator in text_lower) >= 2

def _has_step_formatting(text):
    """Check if text already has step formatting."""
    # Look for numbered lists or bullet points
    step_patterns = [
        r'^\s*\d+\.',  # 1. 2. 3.
        r'^\s*[•\-\*]',  # • - *
        r'Step \d+',  # Step 1, Step 2
        r'\d+\)',  # 1) 2) 3)
    ]
    
    lines = text.split('\n')
    formatted_lines = 0
    
    for line in lines:
        if any(re.search(pattern, line, re.MULTILINE) for pattern in step_patterns):
            formatted_lines += 1
    
    # If more than 1/3 of lines are formatted, consider it already formatted
    return formatted_lines > len(lines) / 3

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
