"""
Punc# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="punctuation"):
        return {"suggestion": f"Punctuation issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return FalseRules
Ensures proper punctuation usage throughout documents.
"""

import re
import logging
from typing import List, Dict, Any

# Import the AI helper
try:
    from .llamaindex_helper import get_rag_suggestion, is_ai_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="punctuation"):
        return {"suggestion": f"Punctuation issue: {issue_text}", "confidence": 0.5}
    def is_ai_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for punctuation issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Comma usage
        comma_issues = _check_comma_usage(sentence)
        for issue in comma_issues:
            rag_response = get_rag_suggestion(
                issue_text="Comma usage issue",
                sentence_context=sentence,
                category="punctuation"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Colon and semicolon usage
        colon_semicolon_issues = _check_colon_semicolon(sentence)
        for issue in colon_semicolon_issues:
            rag_response = get_rag_suggestion(
                issue_text="Colon/semicolon usage issue",
                sentence_context=sentence,
                category="punctuation"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Quotation marks
        quote_issues = _check_quotation_marks(sentence)
        for issue in quote_issues:
            rag_response = get_rag_suggestion(
                issue_text="Quotation mark issue",
                sentence_context=sentence,
                category="punctuation"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Hyphen and dash usage
        hyphen_dash_issues = _check_hyphen_dash(sentence)
        for issue in hyphen_dash_issues:
            rag_response = get_rag_suggestion(
                issue_text="Hyphen/dash usage issue",
                sentence_context=sentence,
                category="punctuation"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 5. Apostrophe usage
        apostrophe_issues = _check_apostrophes(sentence)
        for issue in apostrophe_issues:
            rag_response = get_rag_suggestion(
                issue_text="Apostrophe usage issue",
                sentence_context=sentence,
                category="punctuation"
            )
            suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _split_into_sentences(content: str) -> List[str]:
    """Split content into sentences while preserving formatting within sentences."""
    import re
    
    # Clean up extra whitespace but preserve sentence structure
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Split only on sentence-ending punctuation followed by whitespace and capital letter
    sentences = re.split(r'([.!?]+)\s+(?=[A-Z])', content)
    
    # Reconstruct sentences with their punctuation
    result = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            if sentence.strip():
                result.append(sentence.strip())
        else:
            if sentences[i].strip():
                result.append(sentences[i].strip())
    
    # Handle case where content doesn't end with proper punctuation
    if sentences and not result and content.strip():
        result = [content.strip()]
    
    return result

def _check_comma_usage(sentence: str) -> List[str]:
    """Check for comma usage issues."""
    issues = []
    
    # Missing Oxford comma
    oxford_pattern = r'\b\w+,\s+\w+\s+and\s+\w+\b'
    if re.search(oxford_pattern, sentence):
        # Check if it's missing the Oxford comma
        non_oxford = re.search(r'\b\w+,\s+\w+\s+and\s+\w+\b', sentence)
        if non_oxford and sentence.count(',') == 1:
            issues.append("Consider using Oxford comma for clarity")
    
    # Comma splice
    comma_splice_pattern = r'\b\w+\s*,\s*\w+\s+(is|are|was|were|do|does|did|have|has|had)\b'
    if re.search(comma_splice_pattern, sentence):
        issues.append("Possible comma splice - consider using semicolon or period")
    
    # Missing comma after introductory phrases
    intro_patterns = [
        r'^(However|Therefore|Moreover|Furthermore|Additionally|Consequently),?\s+',
        r'^(In fact|For example|In addition|On the other hand),?\s+',
        r'^(After|Before|When|While|Since|Although|Because)\s+.*?,?\s+'
    ]
    
    for pattern in intro_patterns:
        match = re.search(pattern, sentence)
        if match and ',' not in match.group():
            issues.append("Missing comma after introductory phrase")
    
    return issues

def _check_colon_semicolon(sentence: str) -> List[str]:
    """Check for colon and semicolon usage."""
    issues = []
    
    # Incorrect colon usage
    if ':' in sentence:
        # Check if colon is preceded by complete clause
        colon_parts = sentence.split(':')
        if len(colon_parts) == 2:
            before_colon = colon_parts[0].strip()
            # Simple check for incomplete clause before colon
            if not re.search(r'\b(is|are|was|were|include|includes|following)\s*$', before_colon):
                if not re.search(r'\b(the|these|those|such)\s*$', before_colon):
                    issues.append("Colon should be preceded by a complete clause")
    
    # Semicolon usage
    if ';' in sentence:
        semicolon_parts = sentence.split(';')
        if len(semicolon_parts) == 2:
            # Check if both parts are complete clauses
            for part in semicolon_parts:
                part = part.strip()
                if not re.search(r'\b(is|are|was|were|do|does|did|have|has|had|will|would|can|could)\b', part):
                    issues.append("Semicolon should connect two complete clauses")
                    break
    
    return issues

def _check_quotation_marks(sentence: str) -> List[str]:
    """Check for quotation mark issues."""
    issues = []
    
    # Unmatched quotes
    single_quotes = sentence.count("'")
    double_quotes = sentence.count('"')
    
    if single_quotes % 2 != 0:
        issues.append("Unmatched single quotation marks")
    
    if double_quotes % 2 != 0:
        issues.append("Unmatched double quotation marks")
    
    # Incorrect punctuation placement with quotes
    incorrect_quote_patterns = [
        r'"\s*[.!?]',  # Punctuation outside quotes
        r"'\s*[.!?]",   # Punctuation outside single quotes
    ]
    
    for pattern in incorrect_quote_patterns:
        if re.search(pattern, sentence):
            issues.append("Punctuation should be inside quotation marks")
    
    return issues

def _check_hyphen_dash(sentence: str) -> List[str]:
    """Check for hyphen and dash usage."""
    issues = []
    
    # Skip if sentence ends with a period (normal sentence ending)
    if sentence.strip().endswith('.'):
        # Only check for specific hyphen/dash issues, not general punctuation
        pass
    
    # Missing hyphens in compound modifiers (but not at sentence end)
    compound_pattern = r'\b\w+\s+\w+(?:ed|ing|ly)\s+\w+\b'
    matches = re.finditer(compound_pattern, sentence)
    for match in matches:
        # Check if it's a compound modifier before a noun
        # Skip if the match includes the end of the sentence
        if not '-' in match.group() and not match.group().strip().endswith('.'):
            issues.append(f"Consider hyphenating compound modifier: '{match.group()}'")
    
    # Incorrect dash usage
    # Check for double hyphens that should be em dashes
    if '--' in sentence:
        issues.append("Use em dash (—) instead of double hyphen (--)")
    
    # Check for spaced hyphens that should be em dashes
    # But exclude cases where it might be at sentence boundaries
    spaced_hyphen_pattern = r'\s+-\s+'
    if re.search(spaced_hyphen_pattern, sentence):
        # Make sure this isn't confused with sentence-ending punctuation
        match = re.search(spaced_hyphen_pattern, sentence)
        if match and not sentence[match.end():].strip().startswith('.'):
            issues.append("Use em dash (—) instead of spaced hyphen for breaks in thought")
    
    return issues

def _check_apostrophes(sentence: str) -> List[str]:
    """Check for apostrophe usage issues."""
    issues = []
    
    # Common apostrophe errors
    apostrophe_errors = {
        r"\bits'\b": "its (possessive doesn't need apostrophe)",
        r"\byour's\b": "yours",
        r"\bher's\b": "hers", 
        r"\bour's\b": "ours",
        r"\btheir's\b": "theirs",
        r"\bwho's\b": "whose (if possessive)",
        r"'s\s+(are|were|have|had)\b": "s (plural, not possessive)"
    }
    
    for pattern, correction in apostrophe_errors.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Apostrophe error: '{match.group()}' should be '{correction}'")
    
    # Missing apostrophes in contractions
    missing_apostrophe_patterns = {
        r"\bdont\b": "don't",
        r"\bcant\b": "can't",
        r"\bwont\b": "won't",
        r"\bisnt\b": "isn't",
        r"\barent\b": "aren't",
        r"\bwasnt\b": "wasn't",
        r"\bwerent\b": "weren't",
        r"\bhasnt\b": "hasn't",
        r"\bhavent\b": "haven't",
        r"\bhadnt\b": "hadn't"
    }
    
    for pattern, correction in missing_apostrophe_patterns.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Missing apostrophe: '{match.group()}' should be '{correction}'")
    
    return issues
