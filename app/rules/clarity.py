"""
Clarity and Conciseness Rules
Ensures text is clear, concise, and easy to understand.
"""

import re
import logging
from typing import List, Dict, Any

# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="clarity"):
        return {"suggestion": f"Clarity issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for clarity and conciseness issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Wordy phrases
        wordy_issues = _check_wordy_phrases(sentence)
        for issue in wordy_issues:
            rag_response = get_rag_suggestion(
                issue_text="Wordy phrase detected",
                sentence_context=sentence,
                category="clarity"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Filler words
        filler_issues = _check_filler_words(sentence)
        for issue in filler_issues:
            rag_response = get_rag_suggestion(
                issue_text="Unnecessary filler word",
                sentence_context=sentence,
                category="clarity"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Long sentences
        length_issues = _check_sentence_length(sentence)
        for issue in length_issues:
            rag_response = get_rag_suggestion(
                issue_text="Sentence too long",
                sentence_context=sentence,
                category="clarity"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Vague language
        vague_issues = _check_vague_language(sentence)
        for issue in vague_issues:
            rag_response = get_rag_suggestion(
                issue_text="Vague language",
                sentence_context=sentence,
                category="clarity"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 5. Complex words
        complex_issues = _check_complex_words(sentence)
        for issue in complex_issues:
            rag_response = get_rag_suggestion(
                issue_text="Complex word can be simplified",
                sentence_context=sentence,
                category="clarity"
            )
            suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _split_into_sentences(content: str) -> List[str]:
    """Split content into sentences while preserving formatting within sentences."""
    import re
    
    # Clean up extra whitespace but preserve sentence structure
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Split only on sentence-ending punctuation followed by whitespace and capital letter
    sentences = re.split(r'([.!?]+)\s+(?=[A-Z])', content)
    
    # Reconstruct sentences with their punctuation
    result = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            if sentence.strip():
                result.append(sentence.strip())
        else:
            if sentences[i].strip():
                result.append(sentences[i].strip())
    
    # Handle case where content doesn't end with proper punctuation
    if sentences and not result and content.strip():
        result = [content.strip()]
    
    return result

def _check_wordy_phrases(sentence: str) -> List[str]:
    """Check for wordy phrases that can be simplified."""
    issues = []
    
    # Wordy phrases and their concise alternatives
    wordy_phrases = {
        r'\bin order to\b': 'to',
        r'\bdue to the fact that\b': 'because',
        r'\bin spite of the fact that\b': 'although',
        r'\bfor the purpose of\b': 'for',
        r'\bby means of\b': 'by',
        r'\bin the event that\b': 'if',
        r'\bat this point in time\b': 'now',
        r'\bat the present time\b': 'now',
        r'\bin the near future\b': 'soon',
        r'\ba large number of\b': 'many',
        r'\ba great deal of\b': 'much',
        r'\bit is important to note that\b': 'note that',
        r'\bplease be aware that\b': 'note that',
        r'\bin my opinion\b': 'I think',
        r'\bas a matter of fact\b': 'in fact',
        r'\btake into consideration\b': 'consider',
        r'\bmake a decision\b': 'decide',
        r'\bgive consideration to\b': 'consider',
        r'\bcome to a conclusion\b': 'conclude',
        r'\bmake an assumption\b': 'assume'
    }
    
    for pattern, replacement in wordy_phrases.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            issues.append(f"Wordy phrase: '{match.group()}' → '{replacement}'")
    
    return issues

def _check_filler_words(sentence: str) -> List[str]:
    """Check for unnecessary filler words."""
    issues = []
    
    # Filler words that add little value
    filler_words = [
        r'\bvery\b', r'\bquite\b', r'\breally\b', r'\babsolutely\b',
        r'\bactually\b', r'\bbasically\b', r'\bessentially\b', r'\bobviously\b',
        r'\bclearly\b', r'\bsimply\b', r'\bjust\b', r'\beven\b',
        r'\bpretty\b', r'\brather\b', r'\bfairly\b', r'\bsomewhat\b'
    ]
    
    for pattern in filler_words:
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            # Check if it's being used as an intensifier
            word = match.group().lower()
            if word in ['very', 'quite', 'really', 'absolutely']:
                issues.append(f"Remove unnecessary intensifier: '{match.group()}'")
            else:
                issues.append(f"Remove filler word: '{match.group()}'")
    
    return issues

def _check_sentence_length(sentence: str) -> List[str]:
    """Check for sentences that are too long."""
    issues = []
    
    word_count = len(sentence.split())
    
    # Flag sentences over 25 words
    if word_count > 25:
        issues.append(f"Long sentence ({word_count} words) - consider breaking into shorter sentences")
    
    return issues

def _check_vague_language(sentence: str) -> List[str]:
    """Check for vague language that should be more specific."""
    issues = []
    
    # Vague terms that should be more specific
    vague_terms = {
        r'\bstuff\b': 'specific items',
        r'\bthings\b': 'specific items',
        r'\ba lot\b': 'many/much',
        r'\bkind of\b': 'somewhat',
        r'\bsort of\b': 'somewhat',
        r'\bfairly\b': 'moderately',
        r'\bretty much\b': 'mostly',
        r'\bmore or less\b': 'approximately',
        r'\band so on\b': 'specific examples',
        r'\betc\.\b': 'specific examples',
        r'\bvarious\b': 'specific types',
        r'\bnumerous\b': 'many',
        r'\bseveral\b': 'specific number'
    }
    
    for pattern, suggestion in vague_terms.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            issues.append(f"Vague language: '{match.group()}' → consider '{suggestion}'")
    
    return issues

def _check_complex_words(sentence: str) -> List[str]:
    """Check for complex words that can be simplified."""
    issues = []
    
    # Complex words and simpler alternatives
    complex_words = {
        r'\butilize\b': 'use',
        r'\bfacilitate\b': 'help',
        r'\bdemonstrate\b': 'show',
        r'\bprevious\b': 'earlier',
        r'\bsubsequent\b': 'later',
        r'\bcommence\b': 'begin',
        r'\bterminate\b': 'end',
        r'\bendeavor\b': 'try',
        r'\bascertain\b': 'find out',
        r'\bpurchase\b': 'buy',
        r'\baccommodate\b': 'fit',
        r'\bestablish\b': 'set up',
        r'\bimplement\b': 'carry out',
        r'\bparticipate\b': 'take part',
        r'\brequirement\b': 'need',
        r'\bcomponent\b': 'part',
        r'\bmethodology\b': 'method',
        r'\boptimize\b': 'improve',
        r'\bmaximize\b': 'increase',
        r'\bminimize\b': 'reduce'
    }
    
    for pattern, simpler in complex_words.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            issues.append(f"Complex word: '{match.group()}' → '{simpler}'")
    
    return issues
