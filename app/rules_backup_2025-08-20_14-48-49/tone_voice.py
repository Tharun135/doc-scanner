"""
Rule for checking tone and voice consistency throughout documents.
Ensures consistent professional tone, appropriate formality level, and brand voice.
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
    """Check for tone and voice consistency issues."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "tone_voice_consistency",
            "Check for tone and voice consistency, appropriate formality level, and professional language use."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    doc = process_text(text_content)

    suggestions.extend(check_formality_consistency(text_content))
    suggestions.extend(check_person_consistency(text_content))
    suggestions.extend(check_professional_tone(text_content))
    suggestions.extend(check_sentence_variety(text_content))
    suggestions.extend(check_hedging_language(text_content))

    return suggestions if suggestions else []

def check_formality_consistency(text_content):
    """Check for consistent formality level."""
    suggestions = []
    
    # Informal indicators
    informal_patterns = [
        r'\bkinda\b', r'\bsorta\b', r'\bgonna\b', r'\bwanna\b',
        r'\byeah\b', r'\bnope\b', r'\byep\b', r'\bokay\b', r'\bok\b',
        r'\bawesome\b', r'\bcool\b', r'\bsweet\b', r'\bnice\b',
        r'\bstuff\b', r'\bthings\b', r'\bguys\b', r'\bbunch of\b',
        r'\ba lot of\b', r'\btons of\b', r'\bloads of\b',
        r'\bfairly\b', r'\bpretty\s+\w+\b', r'\bkind of\b', r'\bsort of\b'
    ]
    
    # Very formal indicators
    formal_patterns = [
        r'\btherefore\b', r'\bfurthermore\b', r'\bmoreover\b', r'\bnevertheless\b',
        r'\bhowever\b', r'\bconsequently\b', r'\bsubsequently\b', r'\bnotwithstanding\b',
        r'\bheretofore\b', r'\bwherein\b', r'\bwhereas\b', r'\baforesaid\b',
        r'\bpursuant to\b', r'\bin accordance with\b', r'\bwith regard to\b'
    ]
    
    informal_count = 0
    formal_count = 0
    
    for pattern in informal_patterns:
        matches = re.findall(pattern, text_content, flags=re.IGNORECASE)
        informal_count += len(matches)
    
    for pattern in formal_patterns:
        matches = re.findall(pattern, text_content, flags=re.IGNORECASE)
        formal_count += len(matches)
    
    total_indicators = informal_count + formal_count
    if total_indicators > 5:  # Only check if there are enough indicators
        if informal_count > 0 and formal_count > 0:
            ratio = min(informal_count, formal_count) / max(informal_count, formal_count)
            if ratio > 0.3:  # Mixed formality
                suggestions.append(f"Mixed formality levels detected: {informal_count} informal vs {formal_count} formal indicators. Choose a consistent tone.")
    
    return suggestions

def check_person_consistency(text_content):
    """Check for consistent use of person (1st, 2nd, 3rd)."""
    suggestions = []
    
    # Count different person usages
    first_person = len(re.findall(r'\b(I|we|us|our|my|mine)\b', text_content, flags=re.IGNORECASE))
    second_person = len(re.findall(r'\b(you|your|yours)\b', text_content, flags=re.IGNORECASE))
    third_person_impersonal = len(re.findall(r'\b(one|someone|people|users|customers)\b', text_content, flags=re.IGNORECASE))
    
    total_persons = first_person + second_person + third_person_impersonal
    if total_persons > 10:  # Only check documents with enough person references
        person_types = sum([1 for count in [first_person, second_person, third_person_impersonal] if count > 2])
        
        if person_types > 1:
            suggestions.append(f"Inconsistent person usage: 1st person ({first_person}), 2nd person ({second_person}), impersonal ({third_person_impersonal}). Choose a consistent perspective.")
    
    return suggestions

def check_professional_tone(text_content):
    """Check for unprofessional language or tone."""
    suggestions = []
    
    # Potentially unprofessional words/phrases
    unprofessional_patterns = [
        r'\bobviously\b', r'\bduh\b', r'\bno-brainer\b', r'\bpiece of cake\b',
        r'\bsuper easy\b', r'\btrivial\b', r'\bdead simple\b', r'\bchildish\b',
        r'\bstupid\b', r'\bidiot\b', r'\bdumb\b', r'\bcrazy\b', r'\binsane\b',
        r'\bawesome\b', r'\bamazing\b', r'\bincredible\b', r'\bfantastic\b',
        r'\bhate\b', r'\blove\b', r'\badore\b', r'\bobsessed\b',
        r'\bseriously\?\b', r'\bcome on\b', r'\bget real\b'
    ]
    
    for pattern in unprofessional_patterns:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            word = match.group()
            suggestions.append(f"Consider more professional language: '{word}' may be too casual or subjective for technical documentation.")
    
    # Exclamation mark rule removed - was causing false positives with NOTE/WARNING templates
    
    return suggestions

def check_sentence_variety(text_content):
    """Check for sentence variety and rhythm."""
    suggestions = []
    
    sentences = re.split(r'[.!?]+', text_content)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 5:
        return suggestions
    
    # Check sentence length variety
    word_counts = [len(s.split()) for s in sentences]
    avg_length = sum(word_counts) / len(word_counts)
    
    # Check for too many similar-length sentences
    similar_length_count = sum(1 for wc in word_counts if abs(wc - avg_length) < 3)
    
    if similar_length_count / len(sentences) > 0.7:
        suggestions.append("Consider varying sentence length for better rhythm and readability.")
    
    # Check for too many sentences starting the same way
    sentence_starters = [s.split()[0].lower() for s in sentences if s.split()]
    starter_counts = {}
    for starter in sentence_starters:
        starter_counts[starter] = starter_counts.get(starter, 0) + 1
    
    most_common_starter = max(starter_counts.values()) if starter_counts else 0
    if most_common_starter > len(sentences) * 0.3:
        suggestions.append("Many sentences start with the same word. Consider varying sentence beginnings.")
    
    return suggestions

def check_hedging_language(text_content):
    """Check for appropriate use of hedging language."""
    suggestions = []
    
    # Excessive hedging patterns
    hedging_patterns = [
        r'\bmight\s+possibly\b', r'\bcould\s+perhaps\b', r'\bmay\s+potentially\b',
        r'\bseems\s+to\s+appear\b', r'\bappears\s+to\s+seem\b',
        r'\bperhaps\s+maybe\b', r'\bpossibly\s+might\b'
    ]
    
    for pattern in hedging_patterns:
        matches = re.finditer(pattern, text_content, flags=re.IGNORECASE)
        for match in matches:
            phrase = match.group()
            suggestions.append(f"Excessive hedging: '{phrase}' weakens your message. Choose one qualifier.")
    
    # Check for overuse of uncertainty
    uncertainty_words = [
        'maybe', 'perhaps', 'possibly', 'probably', 'likely', 'seemingly',
        'apparently', 'presumably', 'supposedly', 'allegedly'
    ]
    
    uncertainty_count = 0
    for word in uncertainty_words:
        uncertainty_count += len(re.findall(f'\\b{word}\\b', text_content, flags=re.IGNORECASE))
    
    sentence_count = len(re.findall(r'[.!?]+', text_content))
    if sentence_count > 0 and uncertainty_count / sentence_count > 0.2:
        suggestions.append(f"High use of uncertainty language ({uncertainty_count} instances). Consider being more definitive where appropriate.")
    
    return suggestions
