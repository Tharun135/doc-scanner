"""
Rule for checking document structure and formatting consistency.
Ensures consistent heading levels, list formatting, and document organization.
"""

import re
from bs4 import BeautifulSoup
import html
from .spacy_utils import get_nlp_model, process_text

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

def check(content):
    """Check for document structure and formatting consistency issues."""
    suggestions = []

    # Strip HTML tags from content but preserve structure info
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "document_structure",
            "Check for document structure and formatting consistency issues including heading hierarchy, list formatting, and organizational patterns."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    suggestions.extend(check_heading_hierarchy(content, soup))
    suggestions.extend(check_list_formatting(content, text_content))
    suggestions.extend(check_numbering_consistency(text_content))
    suggestions.extend(check_capitalization_consistency(text_content))
    suggestions.extend(check_spacing_consistency(text_content))

    return suggestions if suggestions else []

def check_heading_hierarchy(content, soup):
    """Check for proper heading hierarchy (H1 -> H2 -> H3, etc.)."""
    suggestions = []
    
    # Find all headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headings:
        return suggestions
    
    heading_levels = []
    for heading in headings:
        level = int(heading.name[1])  # Extract number from h1, h2, etc.
        heading_levels.append((level, heading.get_text().strip()))
    
    # Check for skipped levels
    for i in range(1, len(heading_levels)):
        current_level = heading_levels[i][0]
        prev_level = heading_levels[i-1][0]
        
        if current_level > prev_level + 1:
            suggestions.append(f"Heading hierarchy issue: Skipped from H{prev_level} to H{current_level}. Consider using H{prev_level + 1} instead.")
    
    # Check for multiple H1s
    h1_count = sum(1 for level, _ in heading_levels if level == 1)
    if h1_count > 1:
        suggestions.append(f"Multiple H1 headings found ({h1_count}). Consider using only one H1 per document.")
    
    return suggestions

def check_list_formatting(content, text_content):
    """Check for consistent list formatting."""
    suggestions = []
    
    # Check for inconsistent bullet points
    bullet_patterns = [
        r'^\s*•\s+',     # bullet point
        r'^\s*-\s+',     # dash
        r'^\s*\*\s+',    # asterisk
        r'^\s*\+\s+',    # plus
    ]
    
    bullet_types = []
    lines = text_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for i, pattern in enumerate(bullet_patterns):
            if re.match(pattern, line):
                bullet_types.append((i, line_num, line.strip()[:50]))
    
    # If there are multiple bullet types used, suggest consistency
    if len(set(bt[0] for bt in bullet_types)) > 1:
        suggestions.append("Inconsistent bullet point formatting. Use the same bullet character throughout the document.")
    
    # Check for numbered list inconsistencies
    numbered_patterns = [
        r'^\s*\d+\.\s+',     # 1. format
        r'^\s*\d+\)\s+',     # 1) format
        r'^\s*\(\d+\)\s+',   # (1) format
    ]
    
    numbered_types = []
    for line_num, line in enumerate(lines, 1):
        for i, pattern in enumerate(numbered_patterns):
            if re.match(pattern, line):
                numbered_types.append((i, line_num))
    
    if len(set(nt[0] for nt in numbered_types)) > 1:
        suggestions.append("Inconsistent numbered list formatting. Use the same numbering style throughout.")
    
    return suggestions

def check_numbering_consistency(text_content):
    """Check for consistent step numbering in procedures."""
    suggestions = []
    
    # Find numbered steps
    step_pattern = r'^\s*(?:Step\s+)?(\d+)[\.\)]\s+'
    steps = []
    
    for line_num, line in enumerate(text_content.split('\n'), 1):
        match = re.match(step_pattern, line, re.IGNORECASE)
        if match:
            step_num = int(match.group(1))
            steps.append((step_num, line_num))
    
    if len(steps) > 1:
        # Check for sequential numbering
        expected = 1
        for step_num, line_num in steps:
            if step_num != expected:
                suggestions.append(f"Step numbering issue: Expected step {expected}, found step {step_num} at line {line_num}.")
            expected = step_num + 1
    
    return suggestions

def check_capitalization_consistency(text_content):
    """Check for consistent capitalization in headings and titles."""
    suggestions = []
    
    # Find potential headings (lines that look like titles)
    lines = text_content.split('\n')
    potential_headings = []
    
    for line in lines:
        line = line.strip()
        # Skip empty lines, very long lines, and lines with lowercase words at start
        if (line and 
            len(line) < 100 and 
            not line[0].islower() and
            not re.match(r'^\d+\.', line) and  # Skip numbered items
            not line.startswith(('•', '-', '*', '+'))):  # Skip bullet points
            
            # Check if it looks like a heading (short, no ending punctuation)
            if len(line.split()) <= 8 and not line.endswith(('.', '!', '?', ':')):
                potential_headings.append(line)
    
    if len(potential_headings) > 2:
        # Analyze capitalization patterns
        title_case_count = 0
        sentence_case_count = 0
        all_caps_count = 0
        
        for heading in potential_headings:
            if heading.isupper():
                all_caps_count += 1
            elif is_title_case(heading):
                title_case_count += 1
            elif is_sentence_case(heading):
                sentence_case_count += 1
        
        total = len(potential_headings)
        if title_case_count > 0 and sentence_case_count > 0:
            suggestions.append(f"Mixed capitalization in headings: {title_case_count} title case, {sentence_case_count} sentence case. Consider using consistent capitalization.")
        
        if all_caps_count > 0 and total > all_caps_count:
            suggestions.append("Mixed use of ALL CAPS and regular case in headings. Consider consistent capitalization.")
    
    return suggestions

def check_spacing_consistency(text_content):
    """Check for consistent spacing patterns."""
    suggestions = []
    
    lines = text_content.split('\n')
    
    # Check for inconsistent indentation
    indentation_patterns = set()
    for line in lines:
        if line.strip():  # Non-empty line
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                indentation_patterns.add(leading_spaces)
    
    # If there are many different indentation levels, suggest consistency
    if len(indentation_patterns) > 4:
        suggestions.append("Inconsistent indentation patterns. Consider using consistent spacing (e.g., 2 or 4 spaces).")
    
    # Check for multiple consecutive blank lines
    blank_line_count = 0
    max_consecutive_blanks = 0
    
    for line in lines:
        if not line.strip():
            blank_line_count += 1
            max_consecutive_blanks = max(max_consecutive_blanks, blank_line_count)
        else:
            blank_line_count = 0
    
    if max_consecutive_blanks > 2:
        suggestions.append(f"Excessive blank lines: Found {max_consecutive_blanks} consecutive blank lines. Consider using single blank lines for separation.")
    
    return suggestions

def is_title_case(text):
    """Check if text follows title case (major words capitalized)."""
    words = text.split()
    if not words:
        return False
    
    # First word should be capitalized
    if not words[0][0].isupper():
        return False
    
    # Check other words (excluding articles, prepositions, etc.)
    minor_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'up'}
    
    for word in words[1:]:
        if word.lower() not in minor_words:
            if not word[0].isupper():
                return False
    
    return True

def is_sentence_case(text):
    """Check if text follows sentence case (only first word capitalized)."""
    words = text.split()
    if not words:
        return False
    
    # First word should be capitalized
    if not words[0][0].isupper():
        return False
    
    # Other words should be lowercase (except proper nouns)
    for word in words[1:]:
        # Skip proper nouns and acronyms
        if word.isupper() or (len(word) > 1 and word[0].isupper() and any(c.isupper() for c in word[1:])):
            continue
        if word[0].isupper():
            return False
    
    return True
