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

    # Rule 1: Don't use 'handicap' except in proper names
    matches = re.finditer(r'\bhandicap\b', content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append(f"Avoid using '{match.group()}'; use 'accessible' or specify the disability.")

    # Rule 2: Don't use 'see', 'watch', or 'look at' to mean 'interact with'
    visual_verbs_pattern = r'\b(see|view|look\s+at|watch|observe)\s+(the|this|that)\s+(?:button|link|menu|option|field|image|icon|dialog|window|page|screen|display)'
    matches = re.finditer(visual_verbs_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append(f"Avoid visual-centric language: '{match.group()}' - consider 'select', 'choose', 'access', or 'use' for better accessibility.")

    # Rule 3: Avoid negative terms like 'defect', 'disease', 'abnormal' when talking about disabilities
    negative_terms = [r'\bdefect\b', r'\bdisease\b', r'\babnormal\b']
    for pattern in negative_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid using negative terms like '{match.group()}' when discussing disabilities.")

    # Rule 4: Don't use terms that suggest pity, such as 'victim' or 'suffer from'
    pity_terms = [r'\bvictim\b', r'\bsuffer from\b']
    for pattern in pity_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid terms that suggest pity like '{match.group()}'; use neutral language.")

    # Rule 5: Use 'wheelchair user' instead of 'confined to a wheelchair' or 'wheelchair-bound'
    wheelchair_phrases = [r'\bconfined to a wheelchair\b', r'\bwheelchair[- ]bound\b']
    for pattern in wheelchair_phrases:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use 'wheelchair user' instead of '{match.group()}'.")

    # Rule 6: Use person-first language
    person_first_patterns = [
        (r'\bthe disabled person\b', 'person with a disability'),
        (r'\bthe blind\b', 'people who are blind'),
        (r'\bthe deaf\b', 'people who are deaf'),
        (r'\bthe autistic\b', 'people with autism'),
        (r'\bdisabled people\b', 'people with disabilities'),
        (r'\bhandicapped person\b', 'person with a disability'),
        (r'\bwheelchair bound\b', 'wheelchair user'),
        (r'\bsuffers from\b', 'has'),
        (r'\bafflicted with\b', 'has'),
    ]
    for pattern, suggestion in person_first_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use person-first language: '{match.group()}' → '{suggestion}'")

    # Rule 7: Avoid outdated or offensive terms
    outdated_terms = {
        r'\bretarded\b': 'with intellectual disability',
        r'\bcrip+led?\b': 'person with a mobility disability', 
        r'\binvalid\b': 'person with a disability',
        r'\bmidget\b': 'person with dwarfism',
        r'\bmute\b': 'person who does not speak',
        r'\bnormal people\b': 'people without disabilities',
        r'\bable-bodied\b': 'people without disabilities',
    }
    
    for pattern, alternative in outdated_terms.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid outdated term: '{match.group()}' → '{alternative}'")

    # Rule 8: Check for color-only instructions
    color_only_pattern = r'\b(?:click|select|choose|press)\s+(?:the\s+)?(?:red|green|blue|yellow|orange|purple|pink|gray|grey|black|white)\s+(?:button|link|text|box|icon|arrow)'
    matches = re.finditer(color_only_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append(f"Color-only instruction: '{match.group()}' - add non-visual identifiers (shape, position, label) for accessibility.")

    return suggestions if suggestions else []