"""
Clarity & Conciseness Rules
- Conciseness, plain language, avoiding ambiguity, eliminating filler
"""
import re
from bs4 import BeautifulSoup
import html

# Import LlamaIndex AI system
try:
    from .llamaindex_helper import get_ai_suggestion
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    import logging
    logging.warning("LlamaIndex AI not available for clarity rules")

def check(content):
    """Check for clarity and conciseness issues"""
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Rule 1: Wordy phrases that can be simplified
    wordy_phrases = find_wordy_phrases(text_content)
    for issue in wordy_phrases:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="wordy_phrase",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Wordy phrase: Replace '{issue['phrase']}' with '{issue['replacement']}'"
            suggestions.append(suggestion)
    
    # Rule 2: Filler words and unnecessary intensifiers
    filler_words = find_filler_words(text_content)
    for issue in filler_words:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="filler_words",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Remove filler word: '{issue['word']}' adds no value to the sentence"
            suggestions.append(suggestion)
    
    # Rule 3: Redundant phrases
    redundant_phrases = find_redundant_phrases(text_content)
    for issue in redundant_phrases:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="redundant_phrase",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Redundant phrase: '{issue['phrase']}' can be simplified to '{issue['replacement']}'"
            suggestions.append(suggestion)
    
    # Rule 4: Long sentences (over 25 words)
    long_sentences = find_long_sentences(text_content)
    for issue in long_sentences:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="long_sentence",
                text=issue['sentence'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Long sentence ({issue['word_count']} words): Consider breaking into shorter sentences"
            suggestions.append(suggestion)
    
    # Rule 5: Vague language
    vague_language = find_vague_language(text_content)
    for issue in vague_language:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="vague_language",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Vague language: '{issue['phrase']}' should be more specific"
            suggestions.append(suggestion)
    
    # Rule 6: Nominalization (turning verbs into nouns)
    nominalizations = find_nominalizations(text_content)
    for issue in nominalizations:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="nominalization",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Nominalization: Replace '{issue['nominalization']}' with verb form '{issue['verb_form']}'"
            suggestions.append(suggestion)
    
    return suggestions

def find_wordy_phrases(text):
    """Find wordy phrases that can be simplified"""
    wordy_replacements = {
        "a number of": "several",
        "a majority of": "most",
        "at this point in time": "now",
        "due to the fact that": "because",
        "in order to": "to",
        "in the event that": "if",
        "prior to": "before",
        "subsequent to": "after",
        "with regard to": "about",
        "with the exception of": "except",
        "in spite of the fact that": "although",
        "for the purpose of": "for",
        "in the near future": "soon",
        "at the present time": "now",
        "during the course of": "during",
        "in the process of": "while",
        "make an examination of": "examine",
        "conduct an investigation": "investigate",
        "make a decision": "decide",
        "provide assistance": "help",
        "make an improvement": "improve"
    }
    
    issues = []
    for wordy, concise in wordy_replacements.items():
        pattern = re.compile(re.escape(wordy), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "phrase": match.group(),
                "replacement": concise,
                "context": context.strip()
            })
    
    return issues

def find_filler_words(text):
    """Find unnecessary filler words and intensifiers"""
    filler_patterns = [
        r'\bvery\b',
        r'\bquite\b', 
        r'\breally\b',
        r'\babsolutely\b',
        r'\bactually\b',
        r'\bobviously\b',
        r'\bclearly\b',
        r'\bbasically\b',
        r'\bessentially\b',
        r'\bkind of\b',
        r'\bsort of\b',
        r'\bI think\b',
        r'\bI believe\b',
        r'\bin my opinion\b'
    ]
    
    issues = []
    for pattern in filler_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "word": match.group(),
                "context": context.strip()
            })
    
    return issues

def find_redundant_phrases(text):
    """Find redundant phrases"""
    redundant_replacements = {
        "end result": "result",
        "final outcome": "outcome",
        "past history": "history",
        "future plans": "plans",
        "advance planning": "planning",
        "close proximity": "proximity",
        "completely eliminate": "eliminate",
        "exact same": "same",
        "free gift": "gift",
        "new innovation": "innovation",
        "personal opinion": "opinion",
        "true facts": "facts",
        "various different": "various",
        "whether or not": "whether"
    }
    
    issues = []
    for redundant, replacement in redundant_replacements.items():
        pattern = re.compile(re.escape(redundant), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "phrase": match.group(),
                "replacement": replacement,
                "context": context.strip()
            })
    
    return issues

def find_long_sentences(text):
    """Find sentences longer than 25 words"""
    issues = []
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Ignore very short fragments
            word_count = len(sentence.split())
            if word_count > 25:
                issues.append({
                    "sentence": sentence,
                    "word_count": word_count
                })
    
    return issues

def find_vague_language(text):
    """Find vague language that should be more specific"""
    vague_patterns = [
        r'\bsome\s+\w+',
        r'\bvarious\s+\w+',
        r'\bmany\s+\w+',
        r'\bseveral\s+\w+',
        r'\ba lot of\b',
        r'\bstuff\b',
        r'\bthings\b',
        r'\bit is\s+\w+\s+that\b',
        r'\bthere are\s+\w+\b',
        r'\bthis\b(?!\s+\w+)',  # "this" without a noun
        r'\bthat\b(?!\s+\w+)'   # "that" without a noun
    ]
    
    issues = []
    for pattern in vague_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "phrase": match.group(),
                "context": context.strip()
            })
    
    return issues

def find_nominalizations(text):
    """Find nominalizations that can be converted to verbs"""
    nominalizations = {
        "make a decision": "decide",
        "provide assistance": "help",
        "conduct an analysis": "analyze", 
        "perform an evaluation": "evaluate",
        "make an assumption": "assume",
        "make a recommendation": "recommend",
        "provide an explanation": "explain",
        "make an improvement": "improve",
        "conduct a review": "review",
        "make a comparison": "compare",
        "provide confirmation": "confirm",
        "make a determination": "determine"
    }
    
    issues = []
    for nominalization, verb_form in nominalizations.items():
        pattern = re.compile(re.escape(nominalization), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "nominalization": match.group(),
                "verb_form": verb_form,
                "context": context.strip()
            })
    
    return issues
