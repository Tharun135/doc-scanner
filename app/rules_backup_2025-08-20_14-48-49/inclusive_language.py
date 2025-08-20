"""
Rule for detecting inclusive language issues and promoting diversity-friendly terminology.
Identifies potentially exclusive or biased language and suggests inclusive alternatives.
"""

import re
from bs4 import BeautifulSoup
import html
from .spacy_utils import get_nlp_model, process_text

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

def check(content):
    """Check for inclusive language issues."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "inclusive_language",
            "Check for inclusive language issues, gender-neutral alternatives, and bias-free terminology."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    doc = process_text(text_content)

    # Rule 1: Gender-neutral alternatives
    gendered_terms = {
        r'\bmankind\b': 'humanity, humankind, people',
        r'\bmanmade\b': 'artificial, synthetic, manufactured',
        r'\bman-made\b': 'artificial, synthetic, manufactured',
        r'\bmanpower\b': 'workforce, personnel, staff',
        r'\bman hours\b': 'person hours, work hours',
        r'\bman-hours\b': 'person-hours, work-hours',
        r'\bmanning\b': 'staffing, operating',
        r'\bmanned\b': 'staffed, operated, crewed',
        r'\bunmanned\b': 'automated, uncrewed, remote-controlled',
        r'\bchairman\b': 'chairperson, chair',
        r'\bsalesman\b': 'salesperson, sales representative',
        r'\bbusinessman\b': 'businessperson, entrepreneur',
        r'\bfireman\b': 'firefighter',
        r'\bpoliceman\b': 'police officer',
        r'\bmailman\b': 'mail carrier, postal worker',
        r'\bworkman\b': 'worker, technician',
        r'\bguys\b': 'everyone, folks, team, people',
    }

    for pattern, alternatives in gendered_terms.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Consider gender-neutral alternative: '{term}' → '{alternatives}'")

    # Rule 2: Potentially problematic technical terms
    problematic_tech_terms = {
        r'\bmaster\s+(?:branch|copy|version)\b': 'main branch/copy/version',
        r'\bslave\s+(?:device|process)\b': 'secondary device/process, replica',
        r'\bwhitelist\b': 'allowlist, approved list',
        r'\bblacklist\b': 'blocklist, denied list',
        r'\bdummy\s+(?:data|variable|text)\b': 'placeholder data/variable/text, sample',
        r'\bsanity\s+check\b': 'validation check, verification',
        r'\binsane\b': 'extreme, intensive, comprehensive',
        r'\bcrazy\b': 'unusual, unexpected, extreme',
    }

    for pattern, alternative in problematic_tech_terms.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Consider inclusive alternative: '{term}' → '{alternative}'")

    # Rule 3: Age-related assumptions
    age_assumptions = [
        r'\bdigital natives\b',
        r'\bmillennials\b',
        r'\byoung people\b',
        r'\bolder users\b',
        r'\bseniors\b',
    ]

    for pattern in age_assumptions:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Age assumption: Consider whether '{term}' is necessary or could be more specific about user needs rather than age.")

    # Rule 4: Ability assumptions
    ability_assumptions = {
        r'\bsee\s+(?:the|this|that)\b': 'view, notice, observe',
        r'\bhear\s+(?:the|this|that)\b': 'notice, detect',
        r'\bwalk\s+through\b': 'go through, proceed through',
        r'\bjump\s+to\b': 'go to, navigate to',
        r'\bstanding\s+meeting\b': 'regular meeting, recurring meeting',
    }

    for pattern, alternative in ability_assumptions.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Consider ability-neutral language: '{term}' → '{alternative}'")

    # Rule 5: Cultural assumptions
    cultural_assumptions = [
        r'\bobviously\b',
        r'\bof course\b',
        r'\bclearly\b',
        r'\bsimply\b',
        r'\bjust\b',
        r'\beasily\b',
    ]

    for pattern in cultural_assumptions:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            # Only flag these if they're used in instructional context
            context = get_context_around_match(text_content, match)
            if is_instructional_context(context):
                suggestions.append(f"Avoid assumptions: '{term}' may not be true for all users. Consider more inclusive phrasing.")

    # Rule 6: Family structure assumptions
    family_assumptions = {
        r'\bfamily\s+name\b': 'last name, surname',
        r'\bchristian\s+name\b': 'first name, given name',
        r'\bmother\s+tongue\b': 'native language, first language',
        r'\bgrandfather\s+clause\b': 'legacy provision, exception clause',
    }

    for pattern, alternative in family_assumptions.items():
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Inclusive alternative: '{term}' → '{alternative}'")

    # Rule 7: Economic assumptions
    economic_assumptions = [
        r'\bbuy\s+(?:a|an|the)\s+\w+',
        r'\bpurchase\s+(?:a|an|the)\s+\w+',
        r'\bget\s+(?:a|an|the)\s+premium\b',
        r'\bupgrade\s+to\s+pro\b',
    ]

    for pattern in economic_assumptions:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            term = match.group()
            suggestions.append(f"Economic assumption: Consider that not all users may be able to '{term}'. Provide alternatives when possible.")

    return suggestions if suggestions else []

def get_context_around_match(text, match, context_size=50):
    """Get context around a regex match."""
    start = max(0, match.start() - context_size)
    end = min(len(text), match.end() + context_size)
    return text[start:end]

def is_instructional_context(context):
    """Check if the context suggests instructional or procedural content."""
    instructional_indicators = [
        'step', 'instruction', 'how to', 'guide', 'tutorial',
        'click', 'select', 'choose', 'enter', 'type',
        'follow', 'complete', 'finish', 'start'
    ]
    
    context_lower = context.lower()
    return any(indicator in context_lower for indicator in instructional_indicators)
