"""
Tone and Voice Rules
Ensures appropriate tone for the target audience and consistent voice.
"""

import re
import logging
from typing import List, Dict, Any

# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="tone"):
        return {"suggestion": f"Tone issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for tone and voice issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Imperative mood for instructions
        imperative_issues = _check_imperative_mood(sentence)
        for issue in imperative_issues:
            rag_response = get_rag_suggestion(
                issue_text="Imperative mood for instructions",
                sentence_context=sentence,
                category="tone"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Inclusive language
        inclusive_issues = _check_inclusive_language(sentence)
        for issue in inclusive_issues:
            rag_response = get_rag_suggestion(
                issue_text="Non-inclusive language",
                sentence_context=sentence,
                category="tone"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Professional tone
        tone_issues = _check_professional_tone(sentence)
        for issue in tone_issues:
            rag_response = get_rag_suggestion(
                issue_text="Tone adjustment needed",
                sentence_context=sentence,
                category="tone"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Positive language
        positive_issues = _check_positive_language(sentence)
        for issue in positive_issues:
            rag_response = get_rag_suggestion(
                issue_text="Consider positive language",
                sentence_context=sentence,
                category="tone"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 5. Consistency in voice
        consistency_issues = _check_voice_consistency(sentence, content)
        for issue in consistency_issues:
            rag_response = get_rag_suggestion(
                issue_text="Voice consistency issue",
                sentence_context=sentence,
                category="tone"
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

def _check_imperative_mood(sentence: str) -> List[str]:
    """Check for proper use of imperative mood in instructions."""
    issues = []
    
    # Look for instruction patterns that should use imperative
    instruction_patterns = [
        r'\byou should\b',
        r'\byou need to\b',
        r'\byou must\b',
        r'\byou have to\b',
        r'\byou can\b',
        r'\bit is necessary to\b',
        r'\bplease\s+\w+',
    ]
    
    for pattern in instruction_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            # Check if it's actually giving instructions
            action_words = ['click', 'select', 'enter', 'type', 'choose', 'navigate', 'open', 'close', 'save']
            if any(word in sentence.lower() for word in action_words):
                issues.append(f"Use imperative mood for instructions: '{sentence[:50]}...'")
                break
    
    return issues

def _check_inclusive_language(sentence: str) -> List[str]:
    """Check for inclusive language usage."""
    issues = []
    
    # Non-inclusive terms and better alternatives
    non_inclusive_terms = {
        r'\bguys\b': 'everyone/folks/team',
        r'\bmankind\b': 'humanity/people',
        r'\bmanmade\b': 'artificial/synthetic',
        r'\bmanpower\b': 'workforce/personnel',
        r'\bchairman\b': 'chairperson/chair',
        r'\bfireman\b': 'firefighter',
        r'\bmailman\b': 'mail carrier',
        r'\bpoliceman\b': 'police officer',
        r'\bhe/she\b': 'they',
        r'\bhis/her\b': 'their',
        r'\bhim/her\b': 'them',
        r'\bblind spot\b': 'gap/oversight',
        r'\bdummy\b': 'placeholder/sample',
        r'\bmaster/slave\b': 'primary/secondary',
        r'\bwhitelist\b': 'allowlist',
        r'\bblacklist\b': 'blocklist'
    }
    
    for pattern, alternative in non_inclusive_terms.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Non-inclusive language: '{match.group()}' → consider '{alternative}'")
    
    return issues

def _check_professional_tone(sentence: str) -> List[str]:
    """Check for appropriate professional tone."""
    issues = []
    
    # Overly casual language
    casual_terms = [
        r'\bokay\b', r'\bok\b', r'\byeah\b', r'\byep\b', r'\bnope\b',
        r'\bawesome\b', r'\bcool\b', r'\bsweet\b', r'\bnice\b',
        r'\bstuff\b', r'\bthings\b', r'\bkinda\b', r'\bsorta\b',
        r'\bgonna\b', r'\bwanna\b', r'\bgotta\b'
    ]
    
    for pattern in casual_terms:
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Too casual for professional writing: '{match.group()}'")
    
    # Overly formal language
    formal_terms = {
        r'\bheretofore\b': 'until now',
        r'\bwhereby\b': 'by which',
        r'\bthereafter\b': 'after that',
        r'\bforthwith\b': 'immediately',
        r'\bnotwithstanding\b': 'despite',
        r'\bpursuant to\b': 'according to',
        r'\baforementioned\b': 'mentioned above'
    }
    
    for pattern, alternative in formal_terms.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Overly formal: '{match.group()}' → '{alternative}'")
    
    return issues

def _check_positive_language(sentence: str) -> List[str]:
    """Check for opportunities to use more positive language."""
    issues = []
    
    # Negative constructions that can be made positive
    negative_patterns = {
        r'\bdon\'t forget\b': 'remember',
        r'\bnot difficult\b': 'easy',
        r'\bnot many\b': 'few',
        r'\bnot often\b': 'rarely',
        r'\bnot possible\b': 'impossible',
        r'\bnot able\b': 'unable',
        r'\bnot unlike\b': 'similar to',
        r'\bnot uncommon\b': 'common',
        r'\bnot bad\b': 'good',
        r'\bnot wrong\b': 'correct'
    }
    
    for pattern, positive in negative_patterns.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Use positive language: '{match.group()}' → '{positive}'")
    
    # Problem-focused language
    problem_words = [
        r'\bproblem\b', r'\bissue\b', r'\berror\b', r'\bfailure\b',
        r'\bwrong\b', r'\bbad\b', r'\bterrible\b', r'\bawful\b'
    ]
    
    solution_context = ['solve', 'fix', 'resolve', 'address', 'handle', 'improve']
    
    for pattern in problem_words:
        if re.search(pattern, sentence, re.IGNORECASE):
            # Check if it's in a solution context
            if not any(word in sentence.lower() for word in solution_context):
                match = re.search(pattern, sentence, re.IGNORECASE)
                issues.append(f"Consider solution-focused language instead of: '{match.group()}'")
    
    return issues

def _check_voice_consistency(sentence: str, full_content: str) -> List[str]:
    """Check for consistency in voice (first person, second person, etc.)."""
    issues = []
    
    # Count different voice patterns in the document
    first_person = len(re.findall(r'\b(I|we|our|us|my)\b', full_content, re.IGNORECASE))
    second_person = len(re.findall(r'\b(you|your)\b', full_content, re.IGNORECASE))
    third_person = len(re.findall(r'\b(he|she|they|it|the user|users)\b', full_content, re.IGNORECASE))
    
    total_pronouns = first_person + second_person + third_person
    
    if total_pronouns > 10:  # Only check if there are enough pronouns to matter
        # Check for mixed voice in current sentence
        sentence_first = len(re.findall(r'\b(I|we|our|us|my)\b', sentence, re.IGNORECASE))
        sentence_second = len(re.findall(r'\b(you|your)\b', sentence, re.IGNORECASE))
        sentence_third = len(re.findall(r'\b(he|she|they|it|the user|users)\b', sentence, re.IGNORECASE))
        
        # If this sentence has multiple voice types
        voice_count = sum([1 for x in [sentence_first, sentence_second, sentence_third] if x > 0])
        if voice_count > 1:
            issues.append("Mixed voice in sentence - maintain consistent voice (first, second, or third person)")
        
        # Check if this sentence's voice is inconsistent with document majority
        dominant_voice = max(first_person, second_person, third_person)
        if dominant_voice == first_person and sentence_second > 0:
            issues.append("Inconsistent voice - document primarily uses first person")
        elif dominant_voice == second_person and sentence_first > 0:
            issues.append("Inconsistent voice - document primarily uses second person")
        elif dominant_voice == third_person and (sentence_first > 0 or sentence_second > 0):
            issues.append("Inconsistent voice - document primarily uses third person")
    
    return issues
