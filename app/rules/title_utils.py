"""
Title Detection Utilities
Helper functions to identify titles and headings in content
"""

import re
from bs4 import BeautifulSoup

def is_title_or_heading(text, original_html=None):
    """
    Determine if a given text is likely a title or heading.
    
    Args:
        text (str): The text to check
        original_html (str): Original HTML content for context
    
    Returns:
        bool: True if text appears to be a title/heading
    """
    if not text or len(text.strip()) == 0:
        return False
    
    text = text.strip()
    
    # Check if it's in HTML heading tags
    if original_html:
        soup = BeautifulSoup(original_html, "html.parser")
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            heading_text = heading.get_text().strip()
            if heading_text == text:
                return True
            # Also check if the text is part of a heading (in case of processing differences)
            if text in heading_text or heading_text in text:
                return True
    
    # Check for markdown heading patterns
    if re.match(r'^#+\s+.+$', text):
        return True
    
    # Check for typical title characteristics
    words = text.split()
    
    # Very short text that might be a title
    if len(words) <= 8:  # Increased from 6 to catch more titles
        # Check if it's title case or all caps
        if text.istitle() or text.isupper():
            return True
        
        # Check if it ends without punctuation (typical for titles)
        if not text.endswith(('.', '!', '?', ';', ':')):
            # Check if it contains mostly capitalized words
            capitalized_words = sum(1 for word in words if word and word[0].isupper())
            if capitalized_words >= len(words) * 0.4:  # 40% or more words capitalized
                return True
    
    # Check for section/chapter patterns
    if re.match(r'^(chapter|section|part|appendix|figure|table)\s+\d+', text.lower()):
        return True
    
    # Check for numbered titles like "1. Introduction", "2.1 Overview"
    if re.match(r'^\d+\.(\d+\.)*\s+[A-Z]', text):
        return True
    
    # Check for common title patterns
    if re.match(r'^(introduction|overview|conclusion|summary|getting started|installation|configuration)', text.lower()):
        return True
    
    # Check if the text starts with a title pattern even if it contains more content
    # This handles cases where spaCy combines title and content into one sentence
    first_line = text.split('\n')[0].strip()
    if first_line != text:  # Multi-line text
        # Check if first line looks like a title
        if is_title_or_heading(first_line, original_html):
            return True
        
        # Check if the beginning of the text (even without number) matches title patterns
        if re.match(r'^(basic\s+configuration|getting\s+started|user\s+documentation|installation\s+requirements)', text.lower()):
            return True
    
    return False

def extract_titles_from_html(html_content):
    """
    Extract all titles/headings from HTML content.
    
    Args:
        html_content (str): HTML content
    
    Returns:
        list: List of title texts
    """
    soup = BeautifulSoup(html_content, "html.parser")
    titles = []
    
    # Extract HTML headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for heading in headings:
        titles.append(heading.get_text().strip())
    
    # Extract other potential titles based on formatting
    # This could be extended based on specific markup patterns
    
    return titles
