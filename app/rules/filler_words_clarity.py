"""
Filler Words and Clarity Checker
===============================

Detects and suggests removal of unnecessary filler words and phrases
that weaken writing clarity and conciseness.

Based on reference files for clarity and plain language rules.
"""

import re
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

def check(content):
    """Main filler words and clarity checker function."""
    suggestions = []

    # Strip HTML tags from content but preserve structure info
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "filler_words_clarity",
            "Check for filler words, unnecessary qualifiers, ambiguous terms, and other clarity issues that weaken writing."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    suggestions.extend(check_filler_words(text_content))
    suggestions.extend(check_ambiguous_terms(text_content))
    suggestions.extend(check_redundant_phrases(text_content))
    suggestions.extend(check_unnecessary_qualifiers(text_content))

    return suggestions if suggestions else []

def check_filler_words(text_content):
    """Check for common filler words that add no value."""
    suggestions = []
    
    # Common filler words and their suggested replacements
    filler_words = {
        # Intensity modifiers that often weaken writing
        r'\bvery\s+': {
            'replacement': '',
            'message': "Remove 'very' or use a stronger word. 'Very good' → 'excellent'"
        },
        r'\breally\s+': {
            'replacement': '',
            'message': "Remove 'really' or use a stronger word. 'Really bad' → 'terrible'"
        },
        r'\bquite\s+': {
            'replacement': '',
            'message': "Remove 'quite' or be more specific. 'Quite large' → 'large' or 'enormous'"
        },
        r'\bbasically\s*': {
            'replacement': '',
            'message': "Remove 'basically' - it adds no meaning"
        },
        r'\bactually\s*': {
            'replacement': '',
            'message': "Remove 'actually' unless contrasting with a previous statement"
        },
        
        # Unnecessary phrase extensions
        r'\bin order to\s+': {
            'replacement': 'to ',
            'message': "Use 'to' instead of 'in order to'"
        },
        r'\bdue to the fact that\s+': {
            'replacement': 'because ',
            'message': "Use 'because' instead of 'due to the fact that'"
        },
        r'\bfor the purpose of\s+': {
            'replacement': 'to ',
            'message': "Use 'to' instead of 'for the purpose of'"
        },
        r'\bat this point in time\s*': {
            'replacement': 'now ',
            'message': "Use 'now' instead of 'at this point in time'"
        },
        r'\bin the event that\s+': {
            'replacement': 'if ',
            'message': "Use 'if' instead of 'in the event that'"
        },
        
        # Hedge words that weaken statements
        r'\bsort of\s+': {
            'replacement': '',
            'message': "Remove 'sort of' - be more definitive"
        },
        r'\bkind of\s+': {
            'replacement': '',
            'message': "Remove 'kind of' - be more definitive"
        },
        r'\bpretty much\s+': {
            'replacement': '',
            'message': "Remove 'pretty much' - be more definitive"
        }
    }
    
    for pattern, info in filler_words.items():
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            # Skip if it's in a quote (might be dialogue)
            surrounding_text = text_content[max(0, match.start()-20):match.end()+20]
            if '"' in surrounding_text or "'" in surrounding_text:
                continue
                
            suggestions.append({
                "text": match.group(0).strip(),
                "start": match.start(),
                "end": match.end(),
                "message": info['message']
            })
    
    return suggestions

def check_ambiguous_terms(text_content):
    """Check for vague, ambiguous terms that should be more specific."""
    suggestions = []
    
    # Ambiguous terms that need clarification
    ambiguous_patterns = {
        r'\bsoon\b': "Be specific instead of 'soon': 'within 24 hours', 'next week', etc.",
        r'\bappropriate\b': "Be specific instead of 'appropriate': define what makes it suitable",
        r'\bas needed\b': "Be specific instead of 'as needed': define when and how often",
        r'\bif necessary\b': "Be specific instead of 'if necessary': define the conditions",
        r'\bsome\s+(?:time|where|how)\b': "Be more specific than 'sometime/somewhere/somehow'",
        r'\ba lot of\b': "Be more specific than 'a lot of': use numbers or precise quantities",
        r'\bmany\s+(?:times|people|things)\b': "Be more specific than 'many': use approximate numbers",
        r'\bvarious\s+(?!reasons|ways|methods)': "Be more specific than 'various': list the items or use 'several'",
        r'\betc\.?\s*$': "Avoid ending with 'etc.' - be complete or use 'such as' for examples"
    }
    
    for pattern, message in ambiguous_patterns.items():
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            suggestions.append({
                "text": match.group(0).strip(),
                "start": match.start(),
                "end": match.end(),
                "message": message
            })
    
    return suggestions

def check_redundant_phrases(text_content):
    """Check for redundant phrases that can be simplified."""
    suggestions = []
    
    # Redundant phrases and their simpler alternatives
    redundant_patterns = {
        r'\badvance planning\b': {
            'replacement': 'planning',
            'message': "Use 'planning' instead of 'advance planning' (planning is inherently advance)"
        },
        r'\bfuture plans\b': {
            'replacement': 'plans',
            'message': "Use 'plans' instead of 'future plans' (plans are inherently future)"
        },
        r'\bend result\b': {
            'replacement': 'result',
            'message': "Use 'result' instead of 'end result'"
        },
        r'\bfinal outcome\b': {
            'replacement': 'outcome',
            'message': "Use 'outcome' instead of 'final outcome'"
        },
        r'\bfree gift\b': {
            'replacement': 'gift',
            'message': "Use 'gift' instead of 'free gift' (gifts are inherently free)"
        },
        r'\bpast history\b': {
            'replacement': 'history',
            'message': "Use 'history' instead of 'past history' (history is inherently past)"
        },
        r'\bunexpected surprise\b': {
            'replacement': 'surprise',
            'message': "Use 'surprise' instead of 'unexpected surprise' (surprises are inherently unexpected)"
        },
        r'\brepeat again\b': {
            'replacement': 'repeat',
            'message': "Use 'repeat' instead of 'repeat again'"
        }
    }
    
    for pattern, info in redundant_patterns.items():
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            suggestions.append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "message": info['message']
            })
    
    return suggestions

def check_unnecessary_qualifiers(text_content):
    """Check for unnecessary qualifying words that weaken statements."""
    suggestions = []
    
    # Patterns for unnecessary qualifiers
    qualifier_patterns = {
        r'\bI think that\s+': "Remove 'I think that' for stronger statements",
        r'\bI believe that\s+': "Remove 'I believe that' for stronger statements", 
        r'\bIt seems that\s+': "Remove 'It seems that' for stronger statements",
        r'\bIt appears that\s+': "Remove 'It appears that' for stronger statements",
        r'\bperhaps\s+(?:you|we|they)\s+(?:should|could|might)': "Be more direct - remove 'perhaps' for stronger recommendations",
        r'\bmight want to consider\s+': "Use 'consider' or 'should' instead of 'might want to consider'",
        r'\btend to\s+': "Be more direct - remove 'tend to' if always true",
        r'\bgenerally speaking\s*,?\s*': "Remove 'generally speaking' for cleaner text"
    }
    
    for pattern, message in qualifier_patterns.items():
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            # Don't flag in questions or conditional statements
            sentence_start = text_content.rfind('.', 0, match.start()) + 1
            sentence_end = text_content.find('.', match.end())
            if sentence_end == -1:
                sentence_end = len(text_content)
            
            sentence = text_content[sentence_start:sentence_end].strip()
            
            # Skip if sentence is a question or conditional
            if sentence.strip().endswith('?') or 'if ' in sentence.lower():
                continue
                
            suggestions.append({
                "text": match.group(0).strip(),
                "start": match.start(),
                "end": match.end(),
                "message": message
            })
    
    return suggestions

if __name__ == "__main__":
    # Test the filler words and clarity rules
    test_content = """
    <p>I think that this is very good, basically. You really should consider it.</p>
    <p>In order to complete the task, we need to plan appropriately.</p>
    <p>The end result will be quite impressive, sort of.</p>
    <p>We'll finish soon, perhaps next week or something.</p>
    """
    
    print("🔍 Testing Filler Words and Clarity Rules")
    print("=" * 50)
    
    results = check(test_content)
    
    for i, suggestion in enumerate(results, 1):
        print(f"{i}. {suggestion.get('message', 'No message')}")
        if suggestion.get('text'):
            print(f"   Text: '{suggestion['text']}'")
    
    if not results:
        print("No filler words or clarity issues found!")
