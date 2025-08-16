"""
Formatting and Structure Rules
Ensures consistent formatting and proper document structure.
"""

import re
import logging
from typing import List, Dict, Any

# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="formatting"):
        return {"suggestion": f"Formatting issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for formatting and structure issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # 1. Heading hierarchy
    heading_issues = _check_heading_hierarchy(content)
    for issue in heading_issues:
        rag_response = get_rag_suggestion(
            issue_text="Heading hierarchy issue",
            sentence_context=issue,
            category="formatting"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    # 2. List formatting
    list_issues = _check_list_formatting(content)
    for issue in list_issues:
        rag_response = get_rag_suggestion(
            issue_text="List formatting issue",
            sentence_context=issue,
            category="formatting"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    # 3. Code formatting
    code_issues = _check_code_formatting(content)
    for issue in code_issues:
        rag_response = get_rag_suggestion(
            issue_text="Code formatting issue",
            sentence_context=issue,
            category="formatting"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    # 4. Table formatting
    table_issues = _check_table_formatting(content)
    for issue in table_issues:
        rag_response = get_rag_suggestion(
            issue_text="Table formatting issue",
            sentence_context=issue,
            category="formatting"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    # 5. General formatting
    general_issues = _check_general_formatting(content)
    for issue in general_issues:
        rag_response = get_rag_suggestion(
            issue_text="General formatting issue",
            sentence_context=issue,
            category="formatting"
        )
        suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _check_heading_hierarchy(content: str) -> List[str]:
    """Check for proper heading hierarchy."""
    issues = []
    
    # Check HTML headings
    html_headings = re.findall(r'<h([1-6])[^>]*>(.*?)</h[1-6]>', content, re.IGNORECASE)
    if html_headings:
        levels = [int(level) for level, text in html_headings]
        
        # Check for multiple H1s
        h1_count = levels.count(1)
        if h1_count > 1:
            issues.append("Multiple H1 headings found - use only one H1 per document")
        
        # Check for skipped levels
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                issues.append(f"Skipped heading level: H{levels[i-1]} to H{levels[i]} - maintain proper hierarchy")
    
    # Check Markdown headings
    markdown_headings = re.findall(r'^(#+)\s+(.+)$', content, re.MULTILINE)
    if markdown_headings:
        levels = [len(hashes) for hashes, text in markdown_headings]
        
        # Check for multiple level 1 headings
        if levels.count(1) > 1:
            issues.append("Multiple # headings found - use only one # heading per document")
        
        # Check for skipped levels
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                issues.append(f"Skipped heading level: {levels[i-1]} to {levels[i]} - maintain proper hierarchy")
    
    return issues

def _check_list_formatting(content: str) -> List[str]:
    """Check for proper list formatting."""
    issues = []
    
    # Check for inconsistent list markers
    lines = content.split('\n')
    in_list = False
    list_markers = []
    
    for line in lines:
        line = line.strip()
        
        # Check for bullet list markers
        if re.match(r'^[*+-]\s', line):
            if not in_list:
                in_list = True
                list_markers = []
            marker = line[0]
            list_markers.append(marker)
        elif re.match(r'^\d+\.\s', line):
            # Numbered list
            continue
        elif line == '':
            continue
        else:
            if in_list and len(set(list_markers)) > 1:
                issues.append(f"Inconsistent list markers: {set(list_markers)} - use consistent markers")
            in_list = False
            list_markers = []
    
    # Check for missing spaces after list markers
    improper_lists = re.findall(r'^[*+-]\S', content, re.MULTILINE)
    for match in improper_lists:
        issues.append(f"Missing space after list marker: '{match}'")
    
    # Check for numbered list formatting
    numbered_lists = re.findall(r'^\d+\.\S', content, re.MULTILINE)
    for match in numbered_lists:
        issues.append(f"Missing space after numbered list marker: '{match}'")
    
    return issues

def _check_code_formatting(content: str) -> List[str]:
    """Check for proper code formatting."""
    issues = []
    
    # Check for code blocks without language specification
    code_blocks = re.findall(r'```\n', content)
    if code_blocks:
        issues.append("Code blocks without language specification - specify language for better formatting")
    
    # Check for inline code formatting
    # Look for code-like content that should be formatted as code
    code_patterns = [
        r'\b[a-zA-Z_][a-zA-Z0-9_]*\(\)\b',  # function calls
        r'\b[A-Z_][A-Z0-9_]{2,}\b',         # constants
        r'\bvar\s+\w+\b',                   # variable declarations
        r'\bfunction\s+\w+\b',              # function declarations
    ]
    
    for pattern in code_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Check if it's not already in code formatting
            if f'`{match}`' not in content and f'<code>{match}</code>' not in content:
                issues.append(f"Consider formatting as code: '{match}'")
    
    return issues

def _check_table_formatting(content: str) -> List[str]:
    """Check for proper table formatting."""
    issues = []
    
    # Check HTML tables
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.IGNORECASE | re.DOTALL)
    for table in tables:
        if '<th' not in table.lower():
            issues.append("Table without header cells (th) - add headers for accessibility")
        
        if 'border' not in table.lower() and 'style' not in table.lower():
            issues.append("Table without styling - consider adding borders or CSS styling")
    
    # Check Markdown tables
    markdown_tables = re.findall(r'\|.*\|', content)
    if markdown_tables:
        # Check for alignment
        table_lines = [line for line in content.split('\n') if '|' in line]
        if len(table_lines) > 1:
            # Check for header separator
            has_separator = any('---' in line or ':--' in line for line in table_lines)
            if not has_separator:
                issues.append("Markdown table missing header separator row")
    
    return issues

def _check_general_formatting(content: str) -> List[str]:
    """Check for general formatting issues."""
    issues = []
    
    # Check for excessive whitespace
    if re.search(r'\n\n\n+', content):
        issues.append("Excessive blank lines - use single blank lines for separation")
    
    # Check for trailing whitespace
    lines_with_trailing_space = [i+1 for i, line in enumerate(content.split('\n')) if line.endswith(' ')]
    if lines_with_trailing_space:
        issues.append(f"Lines with trailing whitespace: {lines_with_trailing_space[:5]}")
    
    # Check for inconsistent indentation
    indented_lines = re.findall(r'^[ \t]+', content, re.MULTILINE)
    if indented_lines:
        space_indents = [line for line in indented_lines if line.startswith(' ')]
        tab_indents = [line for line in indented_lines if line.startswith('\t')]
        
        if space_indents and tab_indents:
            issues.append("Mixed indentation - use either spaces or tabs consistently")
    
    # Check for long lines
    lines = content.split('\n')
    long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 100]
    if long_lines:
        issues.append(f"Lines over 100 characters: {long_lines[:3]}")
    
    return issues
