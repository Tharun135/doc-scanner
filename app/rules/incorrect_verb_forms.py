import re
import spacy
from bs4 import BeautifulSoup
import html

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

    # Rule: Detect incorrect verb forms with "-eds" suffix
    incorrect_verb_matches = find_incorrect_verb_forms(text_content)
    
    for match in incorrect_verb_matches:
        incorrect_word = match['incorrect_word']
        correct_word = match['correct_word']
        context = match['context']
        
        # Create suggestion in the expected string format
        suggestion = f"Issue: Incorrect verb form detected\nOriginal sentence: {context}\nAI suggestion: Change '{incorrect_word}' to '{correct_word}'"
        suggestions.append(suggestion)

    return suggestions

def find_incorrect_verb_forms(text):
    """Find incorrect verb forms with -eds suffix."""
    matches = []
    
    # Pattern to find words ending with "-eds" which is typically incorrect
    # This catches "supporteds", "provideds", "createds", etc.
    pattern = r'\b(\w+)eds\b'
    
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        incorrect_word = match.group(0)
        captured_base = match.group(1)  # This might not be the real base
        start_pos = match.start()
        end_pos = match.end()
        
        # Skip proper nouns and common words that legitimately end in "eds"
        if should_skip_word(incorrect_word, captured_base):
            continue
        
        # Try to determine the actual base word by checking common patterns
        actual_base = determine_actual_base_word(incorrect_word)
        
        # Generate the correct form
        correct_word = generate_correct_verb_form(actual_base, incorrect_word)
        
        # Skip if we can't determine a better form
        if not correct_word or correct_word == incorrect_word:
            continue
        
        # Get context around the incorrect word
        context_start = max(0, start_pos - 30)
        context_end = min(len(text), end_pos + 30)
        context = text[context_start:context_end].strip()
        
        # Clean up context to show the relevant sentence fragment
        context = clean_context(context, incorrect_word)
        
        matches.append({
            'incorrect_word': incorrect_word,
            'correct_word': correct_word,
            'context': context,
            'start_pos': start_pos,
            'end_pos': end_pos
        })
    
    return matches

def determine_actual_base_word(incorrect_word):
    """Determine the actual base word from the incorrect form."""
    if not incorrect_word.lower().endswith('eds'):
        return incorrect_word
    
    # Remove 'eds' to get potential base
    potential_base = incorrect_word[:-3]
    
    # Common patterns where the base word needs correction
    base_corrections = {
        'provid': 'provide',
        'creat': 'create', 
        'updat': 'update',
        'generat': 'generate',
        'validat': 'validate',
        'configur': 'configure',
        'execut': 'execute',
        'operat': 'operate',
        'integrat': 'integrate',
        'migrat': 'migrate',
        'customiz': 'customize',
        'optimiz': 'optimize',
        'analyz': 'analyze',
        'initializat': 'initialize',
        'implement': 'implement',
        'establish': 'establish',
        'maintain': 'maintain',
        'develop': 'develop',
        'design': 'design'
    }
    
    potential_lower = potential_base.lower()
    
    # Check for direct corrections
    if potential_lower in base_corrections:
        # Preserve original capitalization
        if incorrect_word[0].isupper():
            return base_corrections[potential_lower].capitalize()
        else:
            return base_corrections[potential_lower]
    
    # If the potential base ends with a consonant and is likely missing an 'e'
    if (len(potential_base) > 3 and 
        potential_base[-1] not in 'aeiou' and 
        potential_base[-2] not in 'aeiou'):
        
        # Try adding 'e' and see if it makes sense
        with_e = potential_base + 'e'
        common_verbs_with_e = {
            'provide', 'create', 'update', 'execute', 'configure', 'operate',
            'generate', 'validate', 'integrate', 'migrate', 'compile', 'delete',
            'complete', 'compute', 'include', 'exclude', 'require', 'acquire'
        }
        
        if with_e.lower() in common_verbs_with_e:
            if incorrect_word[0].isupper():
                return with_e.capitalize()
            else:
                return with_e
    
    # Return the potential base as-is if no corrections needed
    return potential_base

def should_skip_word(word, base_word):
    """Check if this word should be skipped (legitimate words ending in 'eds')."""
    
    word_lower = word.lower()
    base_lower = base_word.lower()
    
    # Skip proper nouns (capitalized words that aren't at sentence start)
    if word[0].isupper():
        return True
    
    # Skip common legitimate words ending in "eds"
    legitimate_words = {
        'leeds', 'seeds', 'needs', 'feeds', 'deeds', 'reeds', 'weeds', 'speeds',
        'breeds', 'creeds', 'bleeds', 'proceeds', 'exceeds', 'succeeds'
    }
    
    if word_lower in legitimate_words:
        return True
    
    # Skip if the base word is very short (likely not a verb)
    if len(base_lower) <= 2:
        return True
    
    # Skip if base word doesn't look like a verb
    non_verb_endings = {'ed', 'er', 'le', 'al', 'ar', 'el', 'il', 'ol', 'ul'}
    if any(base_lower.endswith(ending) for ending in non_verb_endings):
        return True
    
    return False

def generate_correct_verb_form(base_word, incorrect_word):
    """Generate the correct verb form based on context and common patterns."""
    
    # Common verb corrections for -eds forms
    verb_corrections = {
        'support': 'supports',
        'provide': 'provides', 
        'create': 'creates',
        'update': 'updates',
        'process': 'processes',
        'configure': 'configures',
        'execute': 'executes',
        'generate': 'generates',
        'validate': 'validates',
        'initialize': 'initializes',
        'implement': 'implements',
        'establish': 'establishes',
        'maintain': 'maintains',
        'develop': 'develops',
        'design': 'designs',
        'analyze': 'analyzes',
        'optimize': 'optimizes',
        'customize': 'customizes',
        'integrate': 'integrates',
        'migrate': 'migrates',
        'deploy': 'deploys',
        'install': 'installs',
        'manage': 'manages',
        'monitor': 'monitors',
        'control': 'controls',
        'handle': 'handles',
        'operate': 'operates',
        'utilize': 'utilizes',
        'access': 'accesses',
        'connect': 'connects',
        'transfer': 'transfers',
        'transmit': 'transmits',
        'receive': 'receives',
        'send': 'sends',
        'retrieve': 'retrieves',
        'store': 'stores',
        'save': 'saves',
        'load': 'loads',
        'export': 'exports',
        'import': 'imports',
        'compile': 'compiles',
        'debug': 'debugs',
        'test': 'tests',
        'run': 'runs',
        'build': 'builds',
        'start': 'starts',
        'stop': 'stops',
        'pause': 'pauses',
        'resume': 'resumes',
        'restart': 'restarts'
    }
    
    base_lower = base_word.lower()
    
    # Check if we have a direct mapping
    if base_lower in verb_corrections:
        correct_form = verb_corrections[base_lower]
        
        # Preserve original capitalization
        if incorrect_word[0].isupper():
            return correct_form.capitalize()
        else:
            return correct_form
    
    # For words not in our list, try standard conjugation rules
    # Third person singular present tense rules
    correct_form = base_word
    
    if base_lower.endswith('e'):
        correct_form = base_word + 's'
    elif base_lower.endswith('y') and len(base_word) > 1 and base_word[-2] not in 'aeiou':
        correct_form = base_word[:-1] + 'ies'
    elif base_lower.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z', 'o')):
        correct_form = base_word + 'es'
    else:
        correct_form = base_word + 's'
    
    # Preserve original capitalization
    if incorrect_word[0].isupper():
        return correct_form.capitalize()
    else:
        return correct_form

def clean_context(context, incorrect_word):
    """Clean and format the context to show the relevant part clearly."""
    
    # Find the position of the incorrect word in the context
    word_pos = context.lower().find(incorrect_word.lower())
    
    if word_pos != -1:
        # Try to show a complete sentence or phrase
        # Look for sentence boundaries
        before_word = context[:word_pos]
        after_word = context[word_pos + len(incorrect_word):]
        
        # Find the start of the sentence
        sentence_start = 0
        for i, char in enumerate(reversed(before_word)):
            if char in '.!?':
                sentence_start = len(before_word) - i
                break
        
        # Find the end of the sentence
        sentence_end = len(context)
        for i, char in enumerate(after_word):
            if char in '.!?':
                sentence_end = word_pos + len(incorrect_word) + i + 1
                break
        
        # Extract the sentence containing the incorrect word
        sentence = context[sentence_start:sentence_end].strip()
        
        # If the sentence is too long, truncate it intelligently
        if len(sentence) > 100:
            # Keep the incorrect word in the center
            center = word_pos - sentence_start + len(incorrect_word) // 2
            if center > 50:
                start = center - 40
                sentence = "..." + sentence[start:start+80] + "..."
            else:
                sentence = sentence[:80] + "..."
        
        return sentence
    
    # Fallback: return the original context if we can't find the word
    return context[:80] + "..." if len(context) > 80 else context
