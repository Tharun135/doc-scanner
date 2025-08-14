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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    """
    Check for style guide issues using RAG with smart fallback.
    Primary: RAG-enhanced suggestions
    Fallback: Rule-based detection
    """
    
    # Use RAG-enhanced checking if available
    if RAG_HELPER_AVAILABLE:
        rule_patterns = {
            'detect_function': detect_style_guide_issues
        }
        
        fallback_suggestions = [
            "Style issue detected. Consider using concise, clear language and following consistent formatting guidelines."
        ]
        
        return check_with_rag(
            content=content,
            rule_patterns=rule_patterns,
            rule_name="style_guide",
            fallback_suggestions=fallback_suggestions
        )
    
    # Legacy fallback when RAG helper is not available
    return check_legacy_style_guide(content)

def detect_style_guide_issues(content: str, text_content: str):
    """
    Detect style guide issues in text.
    Returns list of detected issues with context.
    """
    import re
    import spacy
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_content)
    except:
        doc = None
    
    # Rule 1: Wordiness patterns
    wordiness_patterns = [
        (r'\bvery\b', "Remove unnecessary intensifier 'very'"),
        (r'\bquite\b', "Remove unnecessary intensifier 'quite'"),
        (r'\babsolutely\b', "Remove unnecessary intensifier 'absolutely'"),
        (r'\breally\b', "Remove unnecessary intensifier 'really'"),
        (r'\butilize\b', "Replace 'utilize' with simpler 'use'"),
        (r'\bprior to\b', "Replace 'prior to' with simpler 'before'"),
        (r'\bendeavor\b', "Replace 'endeavor' with simpler 'try'")
    ]
    
    for pattern, message in wordiness_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Find sentence context
            sentence_context = ""
            if doc:
                match_pos = match.start()
                for sent in doc.sents:
                    if sent.start_char <= match_pos <= sent.end_char:
                        sentence_context = sent.text.strip()
                        break
            
            issues.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "message": f"Style issue: {message}",
                "context": sentence_context or text_content[:200],
                "sentence": sentence_context
            })
    
    # Rule 2: UI terminology issues
    ui_terms = [
        (r'\bpress\b', "Use 'click' instead of 'press' for UI actions"),
        (r'\bmouse over\b', "Use 'hover' instead of 'mouse over'"),
        (r'\bequipments\b', "Use 'equipment' (singular) instead of 'equipments'")
    ]
    
    for pattern, message in ui_terms:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            sentence_context = ""
            if doc:
                match_pos = match.start()
                for sent in doc.sents:
                    if sent.start_char <= match_pos <= sent.end_char:
                        sentence_context = sent.text.strip()
                        break
            
            issues.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "message": f"UI terminology: {message}",
                "context": sentence_context or text_content[:200],
                "sentence": sentence_context
            })
    
    return issues

def check_legacy_style_guide(content):
    """Legacy style guide detection for fallback when RAG is not available."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Basics - Enforce concise wording
    wordiness_patterns = [r'\bvery\b', r'\bquite\b', r'\babsolutely\b', r'\breally\b']
    for pattern in wordiness_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Consider removing '{match.group()}' for conciseness.")

    # Rule 2: Style - Maintain clarity and consistency
    unclear_phrases = [r'\butilize\b', r'\bprior to\b', r'\bendeavor\b']
    for pattern in unclear_phrases:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Consider replacing '{match.group()}' with a simpler alternative.")

    # Rule 3: Length - Keep sentences and titles concise
    # Identify and handle Markdown tables separately
    table_pattern = re.compile(r'^\|.*\|\s*\n(\|[-:]+\|)+', re.MULTILINE)
    table_matches = list(table_pattern.finditer(content))
    table_ranges = []

    # Store table start and end positions
    for table_match in table_matches:
        table_start = table_match.start()
        table_end = content.find('\n\n', table_start)
        if table_end == -1:
            table_end = len(content)
        table_ranges.append((table_start, table_end))

    # Check for long cell content in tables
    for table_start, table_end in table_ranges:
        table_content = content[table_start:table_end]
        table_lines = table_content.split('\n')
        for line in table_lines:
            if line.startswith('|'):
                cells = line.split('|')
                for cell in cells:
                    if len(cell.strip()) > 100:
                        suggestions.append("Consider breaking long cell content into shorter parts for readability.")

    # Rule 4: Capitalization - Maintain consistency
    capitalization_patterns = [r'\blog in\b', r'\blog file\b', r'\bequipment\b']
    for pattern in capitalization_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Ensure proper capitalization for '{match.group()}'.")

    # Rule 5: Grammar and Vocabulary - Avoid redundancy
    redundant_phrases = {"end result": "Use 'result' instead.", "free gift": "Use 'gift' instead."}
    for phrase, message in redundant_phrases.items():
        pattern = rf'\b{phrase}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(message)

    # Rule 6: UI Terminology - Standardize terms
    ui_terms = {
        "press": "Use 'click' instead of 'press' for UI actions.",
        "mouse over": "Use 'hover' instead of 'mouse over'.",
        "equipments": "Use 'equipment' instead of 'equipments'."
    }
    for term, message in ui_terms.items():
        pattern = rf'\b{term}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(message)

    # Rule 7: Time-based vocabulary - Ensure clarity
    time_words = [r'\blast\b', r'\brecent\b', r'\blatest\b']
    for pattern in time_words:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Ensure '{match.group()}' is used correctly to indicate time.")

    # Rule 8: Numbers and Measurements - Standardize formatting
    number_pattern = r'\b([0-9]+) (seconds|minutes|hours|days)\b'
    matches = re.finditer(number_pattern, content)
    for match in matches:
        suggestions.append("Consider formatting numbers consistently, e.g., '5 minutes' instead of 'five minutes'.")

    return suggestions if suggestions else []