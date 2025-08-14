"""
Tone & Voice Rules
- Audience-appropriate tone, imperative mood, inclusive language
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
    logging.warning("LlamaIndex AI not available for tone rules")

def check(content):
    """Check for tone and voice issues"""
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Rule 1: Inappropriate tone for audience
    tone_issues = find_tone_issues(text_content)
    for issue in tone_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="inappropriate_tone",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Tone issue: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 2: Non-inclusive language
    inclusive_issues = find_non_inclusive_language(text_content)
    for issue in inclusive_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="non_inclusive_language",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Non-inclusive language: Replace '{issue['phrase']}' with '{issue['alternative']}'"
            suggestions.append(suggestion)
    
    # Rule 3: Inconsistent voice (should use imperative for instructions)
    voice_issues = find_voice_inconsistency(text_content)
    for issue in voice_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="voice_inconsistency",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Voice inconsistency: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 4: Overly formal or informal language
    formality_issues = find_formality_issues(text_content)
    for issue in formality_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="formality_mismatch",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Formality issue: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 5: Weak or uncertain language
    weak_language = find_weak_language(text_content)
    for issue in weak_language:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="weak_language",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Weak language: {issue['message']}"
            suggestions.append(suggestion)
    
    return suggestions

def find_tone_issues(text):
    """Find inappropriate tone for technical documentation"""
    issues = []
    
    # Overly casual phrases in technical content
    casual_phrases = [
        r'\bguys\b',
        r'\bokay\b',
        r'\byeah\b',
        r'\bumm\b',
        r'\bwhatever\b',
        r'\bstuff like that\b',
        r'\band whatnot\b',
        r'\bpretty much\b',
        r'\btotally\b',
        r'\bawesome\b',
        r'\bcool\b(?!\s+(?:down|off))',  # Exclude "cool down", "cool off"
    ]
    
    for pattern in casual_phrases:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "message": f"Overly casual tone: '{match.group()}' may be too informal for technical documentation",
                "context": context.strip(),
                "phrase": match.group(),
                "type": "too_casual"
            })
    
    # Overly complex/formal phrases
    overly_formal = [
        r'\butilize\b',
        r'\bfacilitate\b',
        r'\bdemonstrate\b',
        r'\bascertain\b',
        r'\benumerate\b',
        r'\bcommence\b',
        r'\bterminate\b',
        r'\bparticipate in\b',
        r'\bin order to\b'
    ]
    
    for pattern in overly_formal:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "message": f"Overly formal: '{match.group()}' could be simplified",
                "context": context.strip(),
                "phrase": match.group(),
                "type": "too_formal"
            })
    
    return issues

def find_non_inclusive_language(text):
    """Find non-inclusive language and suggest alternatives"""
    inclusive_replacements = {
        # Gender-neutral alternatives
        r'\bguys\b': "everyone",
        r'\bmanpower\b': "workforce",
        r'\bmankind\b': "humanity",
        r'\bman-made\b': "artificial",
        r'\bmanual\b': "handbook",  # Only when referring to "manual labor" context
        
        # Ability-inclusive language
        r'\bcrazy\b': "unexpected",
        r'\binsane\b': "extreme",
        r'\bdumb\b': "simple",
        r'\bstupid\b': "ineffective",
        r'\blame\b': "ineffective",
        
        # Racial/cultural sensitivity
        r'\bblacklist\b': "blocklist",
        r'\bwhitelist\b': "allowlist",
        r'\bmaster/slave\b': "primary/secondary",
        r'\bmaster\b(?=\s+(?:branch|copy|list))': "main",
        
        # Age-inclusive
        r'\bguys and gals\b': "everyone",
        
        # Avoid assumptions
        r'\bobviously\b': "clearly",
        r'\bof course\b': "importantly",
        r'\bsimply\b': "directly"
    }
    
    issues = []
    for pattern, alternative in inclusive_replacements.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "phrase": match.group(),
                "alternative": alternative,
                "context": context.strip(),
                "type": "non_inclusive"
            })
    
    return issues

def find_voice_inconsistency(text):
    """Find voice inconsistency, especially in instructional content"""
    issues = []
    
    # Look for mixed imperative and non-imperative instructions
    instruction_indicators = [
        r'step \d+',
        r'first,',
        r'next,',
        r'then,',
        r'finally,',
        r'to \w+',
        r'in order to'
    ]
    
    sentences = re.split(r'[.!?]+', text)
    instruction_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(re.search(pattern, sentence, re.IGNORECASE) for pattern in instruction_indicators):
            instruction_sentences.append(sentence)
    
    # Check if instructional sentences use inconsistent voice
    if len(instruction_sentences) > 1:
        imperative_count = 0
        non_imperative_count = 0
        
        for sentence in instruction_sentences:
            if is_imperative_voice(sentence):
                imperative_count += 1
            else:
                non_imperative_count += 1
        
        if imperative_count > 0 and non_imperative_count > 0:
            issues.append({
                "message": "Mixed voice in instructions - use consistent imperative voice",
                "context": "; ".join(instruction_sentences[:3]),
                "type": "mixed_voice",
                "imperative_count": imperative_count,
                "non_imperative_count": non_imperative_count
            })
    
    return issues

def find_formality_issues(text):
    """Find formality mismatches"""
    issues = []
    
    # Contractions in formal documents
    contractions = re.finditer(r"\w+'\w+", text)
    contraction_count = len(list(contractions))
    
    if contraction_count > 3:  # More than 3 contractions suggests informal tone
        issues.append({
            "message": f"Multiple contractions ({contraction_count}) may be too informal for technical documentation",
            "context": "Various contractions throughout text",
            "type": "too_many_contractions",
            "count": contraction_count
        })
    
    # Overly academic language
    academic_phrases = [
        r'\bmoreover\b',
        r'\bfurthermore\b',
        r'\bhowever\b(?=,)',
        r'\bnevertheless\b',
        r'\bconsequently\b',
        r'\btherefore\b(?=,)',
        r'\bin conclusion\b'
    ]
    
    academic_count = 0
    for pattern in academic_phrases:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        academic_count += len(matches)
    
    if academic_count > 5:  # More than 5 academic transitions
        issues.append({
            "message": f"Overly academic tone ({academic_count} formal transitions) - consider simpler connectors",
            "context": "Multiple formal transitions throughout text",
            "type": "too_academic",
            "count": academic_count
        })
    
    return issues

def find_weak_language(text):
    """Find weak or uncertain language"""
    weak_patterns = [
        r'\bI think\b',
        r'\bI believe\b',
        r'\bmight be\b',
        r'\bcould be\b',
        r'\bmay be\b',
        r'\bperhaps\b',
        r'\bpossibly\b',
        r'\bprobably\b',
        r'\bseems to\b',
        r'\bappears to\b',
        r'\bkind of\b',
        r'\bsort of\b',
        r'\btry to\b(?!\s+(?:catch|understand))',  # Exclude legitimate uses
        r'\battempt to\b'
    ]
    
    issues = []
    for pattern in weak_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "message": f"Weak language: '{match.group()}' undermines confidence",
                "context": context.strip(),
                "phrase": match.group(),
                "type": "weak_language"
            })
    
    return issues

def is_imperative_voice(sentence):
    """Check if a sentence uses imperative voice"""
    sentence = sentence.strip().lower()
    
    # Common imperative starters
    imperative_starters = [
        'click', 'select', 'choose', 'enter', 'type', 'press', 'open', 'close',
        'go', 'navigate', 'scroll', 'drag', 'drop', 'save', 'delete', 'create',
        'add', 'remove', 'edit', 'modify', 'change', 'update', 'install',
        'configure', 'set', 'enable', 'disable', 'start', 'stop', 'run'
    ]
    
    first_word = sentence.split()[0] if sentence.split() else ""
    return first_word in imperative_starters
