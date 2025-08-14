"""
Capi# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="capitalization"):
        return {"suggestion": f"Capitalization issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return Falseon Rules
Ensures proper capitalization throughout documents.
"""

import re
import logging
from typing import List, Dict, Any

# Import the AI helper
try:
    from .llamaindex_helper import get_rag_suggestion, is_ai_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="capitalization"):
        return {"suggestion": f"Capitalization issue: {issue_text}", "confidence": 0.5}
    def is_ai_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for capitalization issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Sentence case issues
        sentence_case_issues = _check_sentence_case(sentence)
        for issue in sentence_case_issues:
            rag_response = get_rag_suggestion(
                issue_text="Sentence case issue",
                sentence_context=sentence,
                category="capitalization"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Proper noun capitalization
        proper_noun_issues = _check_proper_nouns(sentence)
        for issue in proper_noun_issues:
            rag_response = get_rag_suggestion(
                issue_text="Proper noun capitalization",
                sentence_context=sentence,
                category="capitalization"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Acronym capitalization
        acronym_issues = _check_acronyms(sentence)
        for issue in acronym_issues:
            rag_response = get_rag_suggestion(
                issue_text="Acronym capitalization",
                sentence_context=sentence,
                category="capitalization"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Title case issues
        title_case_issues = _check_title_case(sentence)
        for issue in title_case_issues:
            rag_response = get_rag_suggestion(
                issue_text="Title case issue",
                sentence_context=sentence,
                category="capitalization"
            )
            suggestions.append(rag_response.get("suggestion", issue))
    
    # 5. Check headings in HTML/Markdown
    heading_issues = _check_heading_capitalization(content)
    for issue in heading_issues:
        rag_response = get_rag_suggestion(
            issue_text="Heading capitalization issue",
            sentence_context=issue,
            category="capitalization"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _split_into_sentences(content: str) -> List[str]:
    """Split content into sentences."""
    sentences = re.split(r'[.!?]+', content)
    return [s.strip() for s in sentences if s.strip()]

def _check_sentence_case(sentence: str) -> List[str]:
    """Check for sentence case issues."""
    issues = []
    
    # Check if sentence starts with lowercase (except for brand names, code, etc.)
    if sentence and sentence[0].islower():
        # Exceptions for code, variables, etc.
        if not re.match(r'^[a-z]+[A-Z]', sentence[:10]):  # camelCase
            if not re.match(r'^[a-z_]+', sentence[:10]):   # snake_case
                issues.append("Sentence should start with capital letter")
    
    # Check for unnecessary capitalization mid-sentence
    words = sentence.split()
    for i, word in enumerate(words):
        if i > 0 and word[0].isupper():
            # Skip proper nouns, acronyms, and words after colons
            if not _is_proper_noun(word) and not _is_acronym(word):
                if i == 0 or words[i-1][-1] not in ':;':
                    # Check if it's not at the start of a quoted sentence
                    if not re.search(r'["\']$', words[i-1]):
                        issues.append(f"Unnecessary capitalization: '{word}'")
    
    return issues

def _check_proper_nouns(sentence: str) -> List[str]:
    """Check for proper noun capitalization."""
    issues = []
    
    # Common proper nouns that should be capitalized
    proper_nouns = {
        r'\bmicrosoft\b': 'Microsoft',
        r'\bgoogle\b': 'Google',
        r'\bapple\b': 'Apple',
        r'\bamazon\b': 'Amazon',
        r'\bfacebook\b': 'Facebook',
        r'\btwitter\b': 'Twitter',
        r'\blinkedin\b': 'LinkedIn',
        r'\bwindows\b': 'Windows',
        r'\bmac\b': 'Mac',
        r'\blinux\b': 'Linux',
        r'\binternet\b': 'Internet',
        r'\benglish\b': 'English',
        r'\bspanish\b': 'Spanish',
        r'\bfrench\b': 'French',
        r'\bchristmas\b': 'Christmas',
        r'\bmonday\b': 'Monday',
        r'\btuesday\b': 'Tuesday',
        r'\bwednesday\b': 'Wednesday',
        r'\bthursday\b': 'Thursday',
        r'\bfriday\b': 'Friday',
        r'\bsaturday\b': 'Saturday',
        r'\bsunday\b': 'Sunday',
        r'\bjanuary\b': 'January',
        r'\bfebruary\b': 'February',
        r'\bmarch\b': 'March',
        r'\bapril\b': 'April',
        r'\bmay\b': 'May',
        r'\bjune\b': 'June',
        r'\bjuly\b': 'July',
        r'\baugust\b': 'August',
        r'\bseptember\b': 'September',
        r'\boctober\b': 'October',
        r'\bnovember\b': 'November',
        r'\bdecember\b': 'December'
    }
    
    for pattern, correct_form in proper_nouns.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            if match.group() != correct_form:
                issues.append(f"Proper noun should be capitalized: '{match.group()}' → '{correct_form}'")
    
    return issues

def _check_acronyms(sentence: str) -> List[str]:
    """Check for acronym capitalization."""
    issues = []
    
    # Common acronyms that should be all caps
    acronyms = {
        r'\bapi\b': 'API',
        r'\burl\b': 'URL',
        r'\buri\b': 'URI',
        r'\bhtml\b': 'HTML',
        r'\bcss\b': 'CSS',
        r'\bjs\b': 'JS',
        r'\bxml\b': 'XML',
        r'\bjson\b': 'JSON',
        r'\bhttp\b': 'HTTP',
        r'\bhttps\b': 'HTTPS',
        r'\bftp\b': 'FTP',
        r'\bssh\b': 'SSH',
        r'\bsql\b': 'SQL',
        r'\bpdf\b': 'PDF',
        r'\bcsv\b': 'CSV',
        r'\bzip\b': 'ZIP',
        r'\bgif\b': 'GIF',
        r'\bjpeg\b': 'JPEG',
        r'\bpng\b': 'PNG',
        r'\bsvg\b': 'SVG',
        r'\bai\b': 'AI',
        r'\bml\b': 'ML',
        r'\biot\b': 'IoT',
        r'\bvpn\b': 'VPN',
        r'\bdns\b': 'DNS',
        r'\btcp\b': 'TCP',
        r'\budp\b': 'UDP',
        r'\bip\b': 'IP',
        r'\bmac\b': 'MAC',
        r'\bram\b': 'RAM',
        r'\brom\b': 'ROM',
        r'\bcpu\b': 'CPU',
        r'\bgpu\b': 'GPU',
        r'\bssd\b': 'SSD',
        r'\bhdd\b': 'HDD',
        r'\busb\b': 'USB',
        r'\bhdmi\b': 'HDMI'
    }
    
    for pattern, correct_form in acronyms.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            if match.group() != correct_form:
                issues.append(f"Acronym should be capitalized: '{match.group()}' → '{correct_form}'")
    
    return issues

def _check_title_case(sentence: str) -> List[str]:
    """Check for title case issues in headings."""
    issues = []
    
    # This is primarily for checking if title case is used inappropriately
    # Generally, we prefer sentence case for most headings
    
    # Check for excessive title case
    words = sentence.split()
    if len(words) > 2:
        capitalized_count = sum(1 for word in words if word and word[0].isupper())
        if capitalized_count / len(words) > 0.7:  # More than 70% capitalized
            # Check if it's not proper nouns/acronyms
            non_proper_caps = 0
            for word in words:
                if word and word[0].isupper() and not _is_proper_noun(word) and not _is_acronym(word):
                    if word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'for', 'nor', 'so', 'yet']:
                        non_proper_caps += 1
            
            if non_proper_caps > 3:
                issues.append("Consider using sentence case instead of title case for better readability")
    
    return issues

def _check_heading_capitalization(content: str) -> List[str]:
    """Check heading capitalization in HTML/Markdown."""
    issues = []
    
    # HTML headings
    html_headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
    for heading in html_headings:
        # Remove HTML tags from heading text
        clean_heading = re.sub(r'<[^>]+>', '', heading)
        if clean_heading:
            # Check if it's all lowercase (should be sentence case)
            if clean_heading.islower():
                issues.append(f"Heading should use sentence case: '{clean_heading}'")
            # Check for excessive title case
            elif _has_excessive_title_case(clean_heading):
                issues.append(f"Consider sentence case for heading: '{clean_heading}'")
    
    # Markdown headings
    markdown_headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
    for heading in markdown_headings:
        if heading.islower():
            issues.append(f"Heading should use sentence case: '{heading}'")
        elif _has_excessive_title_case(heading):
            issues.append(f"Consider sentence case for heading: '{heading}'")
    
    return issues

def _is_proper_noun(word: str) -> bool:
    """Check if a word is likely a proper noun."""
    proper_noun_patterns = [
        r'^[A-Z][a-z]+$',  # Standard proper noun pattern
        r'^[A-Z]{2,}$',    # Acronyms
        r'^[A-Z][a-z]*[A-Z]',  # CamelCase (brand names, etc.)
    ]
    
    # Known proper nouns
    known_proper = [
        'Microsoft', 'Google', 'Apple', 'Amazon', 'Facebook', 'Twitter',
        'Windows', 'Mac', 'Linux', 'Internet', 'Monday', 'Tuesday',
        'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    if word in known_proper:
        return True
    
    for pattern in proper_noun_patterns:
        if re.match(pattern, word):
            return True
    
    return False

def _is_acronym(word: str) -> bool:
    """Check if a word is likely an acronym."""
    return len(word) > 1 and word.isupper()

def _has_excessive_title_case(text: str) -> bool:
    """Check if text has excessive title case."""
    words = text.split()
    if len(words) < 3:
        return False
    
    capitalized_count = sum(1 for word in words if word and word[0].isupper())
    return capitalized_count / len(words) > 0.6
