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

    # Rule: Detect repeated consecutive words (e.g., "can can", "the the", "is is")
    repeated_word_matches = find_repeated_words(text_content)
    
    for match in repeated_word_matches:
        word = match['word']
        full_match = match['full_match']
        context = match['context']
        
        # Create suggestion in the expected string format similar to other rules
        suggestion = f"Issue: Repeated word detected\nOriginal sentence: {context}\nAI suggestion: Remove the duplicate '{word}' for clarity"
        suggestions.append(suggestion)

    return suggestions

def find_repeated_words(text):
    """Find repeated consecutive words in text."""
    matches = []
    
    # Pattern to find repeated words (case-insensitive)
    # This pattern captures word boundaries to avoid partial matches
    pattern = r'\b(\w+)\s+\1\b'
    
    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        word = match.group(1).lower()
        full_match = match.group(0)
        start_pos = match.start()
        end_pos = match.end()
        
        # Skip intentional repetitions (common cases)
        if should_skip_repetition(word, text, start_pos):
            continue
        
        # Get context around the repeated word (30 characters before and after)
        context_start = max(0, start_pos - 30)
        context_end = min(len(text), end_pos + 30)
        context = text[context_start:context_end].strip()
        
        # Clean up context to show only the relevant sentence fragment
        context = clean_context(context, full_match)
        
        matches.append({
            'word': word,
            'full_match': full_match,
            'context': context,
            'start_pos': start_pos,
            'end_pos': end_pos
        })
    
    return matches

def should_skip_repetition(word, text, start_pos):
    """Check if this repetition should be skipped (intentional repetitions)."""
    
    # Don't skip common short words that are likely mistakes when repeated
    common_mistake_words = {'is', 'it', 'in', 'on', 'to', 'of', 'or', 'at', 'be', 'we', 'he', 'me'}
    
    # Skip very short words EXCEPT common mistake words
    if len(word) <= 2 and word.lower() not in common_mistake_words:
        return True
    
    # Skip common intentional repetitions
    intentional_repetitions = {
        'very', 'so', 'no', 'yes', 'well', 'now', 'oh', 'ah', 'ha'
    }
    
    if word.lower() in intentional_repetitions:
        return True
    
    # Skip if it appears to be in a title or heading (all caps or title case)
    context_window = 50
    context_start = max(0, start_pos - context_window)
    context_end = min(len(text), start_pos + len(word) * 2 + context_window)
    context = text[context_start:context_end]
    
    # Check if the context suggests this is a title/heading
    if context.isupper() or (context.count('.') == 0 and context.count('\n') > 0):
        return True
    
    return False

def clean_context(context, full_match):
    """Clean and format the context to show the relevant part clearly."""
    
    # Find the position of the repeated word in the context
    match_pos = context.find(full_match)
    
    if match_pos != -1:
        # Try to show a complete sentence or phrase
        # Look for sentence boundaries
        before_match = context[:match_pos]
        after_match = context[match_pos + len(full_match):]
        
        # Find the start of the sentence
        sentence_start = 0
        for i, char in enumerate(reversed(before_match)):
            if char in '.!?':
                sentence_start = len(before_match) - i
                break
        
        # Find the end of the sentence
        sentence_end = len(context)
        for i, char in enumerate(after_match):
            if char in '.!?':
                sentence_end = match_pos + len(full_match) + i + 1
                break
        
        # Extract the sentence containing the repeated word
        sentence = context[sentence_start:sentence_end].strip()
        
        # If the sentence is too long, truncate it intelligently
        if len(sentence) > 100:
            # Keep the repeated word in the center
            center = match_pos - sentence_start + len(full_match) // 2
            if center > 50:
                start = center - 40
                sentence = "..." + sentence[start:start+80] + "..."
            else:
                sentence = sentence[:80] + "..."
        
        return sentence
    
    # Fallback: return the original context if we can't find the match
    return context[:80] + "..." if len(context) > 80 else context
