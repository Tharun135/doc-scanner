"""
Grammar & Syntax Rules
- Sentence structure, subject-verb agreement, passive vs active voice, tense, modifiers
"""
import re
import spacy
from bs4 import BeautifulSoup
import html

# Import LlamaIndex AI system
try:
    from .llamaindex_helper import get_ai_suggestion
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    import logging
    logging.warning("LlamaIndex AI not available for grammar rules")

# Load spaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    nlp = None
    SPACY_AVAILABLE = False

def check(content):
    """Check for grammar and syntax issues"""
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Rule 1: Subject-verb disagreement
    subject_verb_issues = find_subject_verb_disagreement(text_content)
    for issue in subject_verb_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="subject_verb_disagreement",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Subject-verb disagreement: '{issue['subject']}' requires '{issue['correct_verb']}' instead of '{issue['incorrect_verb']}'"
            suggestions.append(suggestion)
    
    # Rule 2: Passive voice detection
    passive_voice_issues = find_passive_voice(text_content)
    for issue in passive_voice_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="passive_voice",
                text=issue['sentence'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Passive voice detected: Consider rewriting '{issue['sentence']}' in active voice"
            suggestions.append(suggestion)
    
    # Rule 3: Misplaced modifiers
    modifier_issues = find_misplaced_modifiers(text_content)
    for issue in modifier_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="misplaced_modifier",
                text=issue['sentence'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Misplaced modifier: '{issue['modifier']}' should be closer to '{issue['target']}'"
            suggestions.append(suggestion)
    
    # Rule 4: Tense consistency
    tense_issues = find_tense_inconsistency(text_content)
    for issue in tense_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="tense_inconsistency",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Tense inconsistency: Mixed tenses detected in paragraph"
            suggestions.append(suggestion)
    
    # Rule 5: Compound adjective hyphens
    hyphen_issues = find_compound_adjective_issues(text_content)
    for issue in hyphen_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="compound_adjective",
                text=issue['phrase'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Missing hyphens in compound adjectives: '{issue['phrase']}' should be hyphenated"
            suggestions.append(suggestion)
    
    return suggestions

def find_subject_verb_disagreement(text):
    """Find subject-verb disagreement issues"""
    issues = []
    if not SPACY_AVAILABLE:
        return issues
    
    doc = nlp(text)
    for sent in doc.sents:
        # Look for subject-verb disagreement patterns
        for token in sent:
            if token.dep_ == "nsubj":
                verb = token.head
                if verb.pos_ == "VERB":
                    # Check for disagreement patterns
                    if token.tag_ in ["NNS", "NNPS"] and verb.tag_ in ["VBZ"]:  # Plural subject + singular verb
                        issues.append({
                            "subject": token.text,
                            "incorrect_verb": verb.text,
                            "correct_verb": get_correct_verb_form(verb.lemma_, True),
                            "context": sent.text
                        })
    return issues

def find_passive_voice(text):
    """Find passive voice constructions"""
    issues = []
    if not SPACY_AVAILABLE:
        return issues
    
    doc = nlp(text)
    for sent in doc.sents:
        # Look for passive voice patterns (be + past participle)
        for token in sent:
            if token.lemma_ in ["be", "get"] and token.head.tag_ == "VBN":
                issues.append({
                    "sentence": sent.text,
                    "passive_construction": f"{token.text} {token.head.text}"
                })
    return issues

def find_misplaced_modifiers(text):
    """Find misplaced modifier issues"""
    issues = []
    # This would require more sophisticated NLP analysis
    # For now, return empty list
    return issues

def find_tense_inconsistency(text):
    """Find tense inconsistency issues"""
    issues = []
    if not SPACY_AVAILABLE:
        return issues
    
    doc = nlp(text)
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(para.strip()) > 50:  # Only check substantial paragraphs
            para_doc = nlp(para)
            tenses = []
            for token in para_doc:
                if token.pos_ == "VERB" and token.tag_ in ["VBD", "VBZ", "VBP", "VBN", "VBG"]:
                    tenses.append(token.tag_)
            
            # Check for mixed tenses
            if len(set(tenses)) > 2:  # More than 2 different tenses
                issues.append({
                    "context": para[:100] + "...",
                    "tenses_found": list(set(tenses))
                })
    
    return issues

def find_compound_adjective_issues(text):
    """Find compound adjectives that need hyphens"""
    issues = []
    
    # Common compound adjective patterns that should be hyphenated
    patterns = [
        r'\b(\w+)-(\w+)\s+(\w+)\b',  # Already hyphenated (good)
        r'\b(well|high|low|long|short|fast|slow)\s+(known|quality|level|term|range|speed)\s+\w+\b',
        r'\b(state|world|top|first|second|third)\s+(of|class|rate|level)\s+\w+\b',
        r'\b(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\s+(one|two|three|four|five|six|seven|eight|nine)\b'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if '-' not in match.group():  # Only flag if not already hyphenated
                issues.append({
                    "phrase": match.group(),
                    "suggested": match.group().replace(' ', '-', 1)
                })
    
    return issues

def get_correct_verb_form(verb_lemma, is_plural):
    """Get the correct verb form based on subject plurality"""
    if is_plural:
        return verb_lemma  # Base form for plural
    else:
        # Add 's' for singular third person
        if verb_lemma.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return verb_lemma + 'es'
        elif verb_lemma.endswith('y') and verb_lemma[-2] not in 'aeiou':
            return verb_lemma[:-1] + 'ies'
        else:
            return verb_lemma + 's'
