"""
Utility functions for formatting AI suggestions consistently across all rules.
"""

def format_suggestion(issue, original_sentence, ai_suggestion):
    """
    Format a suggestion using the standard structure:
    Issue:
    Original sentence:
    AI suggestion:
    
    Args:
        issue (str): Brief description of the issue
        original_sentence (str): The original sentence that triggered the rule
        ai_suggestion (str): The AI's suggested improvement
    
    Returns:
        str: Formatted suggestion string
    """
    return f"Issue: {issue}\nOriginal sentence: {original_sentence}\nAI suggestion: {ai_suggestion}"

def find_sentence_containing_match(doc, match_start, match_end):
    """
    Find the sentence in a spaCy doc that contains a regex match.
    
    Args:
        doc: spaCy doc object
        match_start (int): Start position of the match
        match_end (int): End position of the match
    
    Returns:
        str: The sentence containing the match, or empty string if not found
    """
    for sent in doc.sents:
        if sent.start_char <= match_start <= sent.end_char:
            return sent.text.strip()
    return ""

def find_sentence_containing_text(doc, text):
    """
    Find the sentence in a spaCy doc that contains specific text.
    
    Args:
        doc: spaCy doc object
        text (str): Text to search for
    
    Returns:
        str: The sentence containing the text, or empty string if not found
    """
    for sent in doc.sents:
        if text.lower() in sent.text.lower():
            return sent.text.strip()
    return ""
