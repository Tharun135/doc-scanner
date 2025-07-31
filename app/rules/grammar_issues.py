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
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    nlp = None
    SPACY_AVAILABLE = False

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Rule 1: Missing hyphens in compound adjectives
    compound_adjective_issues = find_compound_adjective_issues(text_content)
    for issue in compound_adjective_issues:
        suggestion = f"Missing hyphens in compound adjectives: '{issue['phrase']}' should be hyphenated"
        suggestions.append(suggestion)

    # Rule 2: Subject-verb disagreement 
    subject_verb_issues = find_subject_verb_disagreement(text_content)
    for issue in subject_verb_issues:
        suggestion = f"Subject-verb disagreement: '{issue['subject']}' requires '{issue['correct_verb']}' instead of '{issue['incorrect_verb']}'"
        suggestions.append(suggestion)

    # Rule 3: Unclear pronoun reference
#    pronoun_issues = find_unclear_pronoun_reference(text_content)
#    for issue in pronoun_issues:
#        suggestion = f"Issue: Unclear pronoun reference\nOriginal sentence: {issue['context']}\nAI suggestion: The pronoun '{issue['pronoun']}' has an unclear antecedent. Specify what it refers to."
#        suggestions.append(suggestion)

    # Rule 4: Misplaced modifiers
#    modifier_issues = find_misplaced_modifiers(text_content)
#    for issue in modifier_issues:
#        suggestion = f"Issue: Misplaced modifier\nOriginal sentence: {issue['context']}\nAI suggestion: The modifier '{issue['modifier']}' should be placed closer to the word it modifies"
#        suggestions.append(suggestion)

#    return suggestions

def find_compound_adjective_issues(text):
    """Find missing hyphens in compound adjectives."""
    issues = []
    
    # Pattern for compound adjectives without hyphens
    # Examples: "vendor and device specific", "user and system level", "real time data"
    patterns = [
        r'\b(\w+)\s+and\s+(\w+)\s+(specific|level|based|related|oriented|compatible|enabled|aware|driven|focused)\b',
        r'\b(real)\s+(time)\s+(\w+)\b',
        r'\b(high)\s+(level|quality|performance|speed)\s+(\w+)\b',
        r'\b(user)\s+(friendly|defined|specific)\s+(\w+)\b',
        r'\b(cross)\s+(platform|browser|device)\s+(\w+)\b',
        r'\b(multi)\s+(user|platform|device|threaded)\s+(\w+)\b',
        r'\b(third)\s+(party)\s+(\w+)\b',
        r'\b(open)\s+(source)\s+(\w+)\b'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start_pos = match.start()
            end_pos = match.end()
            
            # Get context
            context_start = max(0, start_pos - 20)
            context_end = min(len(text), end_pos + 20)
            context = text[context_start:context_end].strip()
            
            issues.append({
                'type': 'compound_adjective',
                'context': context,
                'phrase': match.group(0),
                'start': start_pos,
                'end': end_pos
            })
    
    return issues

def find_subject_verb_disagreement(text):
    """Find subject-verb disagreement issues."""
    issues = []
    
    if not SPACY_AVAILABLE or not nlp:
        return issues
    
    try:
        doc = nlp(text)
        
        for sent in doc.sents:
            # Look for subject-verb pairs
            for token in sent:
                if token.dep_ == "nsubj":  # nominal subject
                    verb = token.head
                    if verb.pos_ == "VERB":
                        # Check for common disagreement patterns
                        subject_text = token.text.lower()
                        verb_text = verb.text.lower()
                        
                        # Plural subjects with singular verbs
                        if (subject_text.endswith('s') and not subject_text.endswith('ss') and 
                            verb_text.endswith('s') and verb.tag_ == "VBZ"):
                            
                            context = sent.text.strip()
                            correct_verb = get_correct_verb_form(verb_text, is_plural=True)
                            
                            issues.append({
                                'type': 'subject_verb_disagreement',
                                'context': context,
                                'subject': subject_text,
                                'incorrect_verb': verb_text,
                                'correct_verb': correct_verb
                            })
    except Exception:
        pass
    
    return issues

def find_unclear_pronoun_reference(text):
    """Find unclear pronoun references."""
    issues = []
    
    if not SPACY_AVAILABLE or not nlp:
        return issues
    
    try:
        doc = nlp(text)
        
        for sent in doc.sents:
            pronouns = []
            nouns = []
            
            for token in sent:
                if token.pos_ == "PRON" and token.text.lower() in ['it', 'this', 'that', 'they', 'them']:
                    pronouns.append(token)
                elif token.pos_ == "NOUN":
                    nouns.append(token)
            
            # If there are multiple nouns and ambiguous pronouns
            if len(nouns) > 2 and len(pronouns) > 0:
                for pronoun in pronouns:
                    context = sent.text.strip()
                    issues.append({
                        'type': 'unclear_pronoun',
                        'context': context,
                        'pronoun': pronoun.text
                    })
    except Exception:
        pass
    
    return issues

def find_misplaced_modifiers(text):
    """Find misplaced modifiers."""
    issues = []
    
    # Common patterns for misplaced modifiers
    patterns = [
        r'\b(only|just|nearly|almost|even|also)\s+(\w+)\s+(\w+)\s+(\w+)\b',
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            modifier = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            
            # Get context
            context_start = max(0, start_pos - 20)
            context_end = min(len(text), end_pos + 20)
            context = text[context_start:context_end].strip()
            
            issues.append({
                'type': 'misplaced_modifier',
                'context': context,
                'modifier': modifier
            })
    
    return issues

def get_correct_verb_form(verb, is_plural=False):
    """Get the correct verb form based on subject plurality."""
    verb_corrections = {
        'is': 'are' if is_plural else 'is',
        'was': 'were' if is_plural else 'was',
        'has': 'have' if is_plural else 'has',
        'does': 'do' if is_plural else 'does'
    }
    
    if verb in verb_corrections:
        return verb_corrections[verb]
    
    # For regular verbs, remove 's' for plural subjects
    if is_plural and verb.endswith('s') and not verb.endswith('ss'):
        return verb[:-1]
    
    return verb
