"""
Formatting & Structure Rules
- Headings, lists, code formatting, UI element styling
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
    logging.warning("LlamaIndex AI not available for formatting rules")

def check(content):
    """Check for formatting and structure issues"""
    suggestions = []
    
    # Parse HTML content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Rule 1: Heading hierarchy issues
    heading_issues = find_heading_hierarchy_issues(soup)
    for issue in heading_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="heading_hierarchy",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Heading hierarchy: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 2: List formatting issues
    list_issues = find_list_formatting_issues(soup, text_content)
    for issue in list_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="list_formatting",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"List formatting: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 3: Code formatting issues
    code_issues = find_code_formatting_issues(soup, text_content)
    for issue in code_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="code_formatting",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Code formatting: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 4: Table formatting issues
    table_issues = find_table_formatting_issues(soup)
    for issue in table_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="table_formatting",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Table formatting: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 5: Paragraph structure issues
    paragraph_issues = find_paragraph_structure_issues(text_content)
    for issue in paragraph_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="paragraph_structure",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Paragraph structure: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 6: White space and layout issues
    whitespace_issues = find_whitespace_issues(text_content)
    for issue in whitespace_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="whitespace",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Whitespace: {issue['message']}"
            suggestions.append(suggestion)
    
    return suggestions

def find_heading_hierarchy_issues(soup):
    """Find heading hierarchy problems"""
    issues = []
    
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if not headings:
        return issues
    
    previous_level = 0
    for heading in headings:
        current_level = int(heading.name[1])  # Extract number from h1, h2, etc.
        
        # Check for skipped levels
        if current_level > previous_level + 1:
            issues.append({
                "message": f"Skipped heading level: {heading.name} follows h{previous_level}",
                "context": heading.get_text()[:50],
                "current_level": current_level,
                "previous_level": previous_level
            })
        
        # Check for empty headings
        if not heading.get_text().strip():
            issues.append({
                "message": "Empty heading found",
                "context": str(heading),
                "level": current_level
            })
        
        previous_level = current_level
    
    # Check for missing H1
    if headings and headings[0].name != 'h1':
        issues.append({
            "message": "Document should start with H1 heading",
            "context": headings[0].get_text()[:50],
            "first_heading": headings[0].name
        })
    
    return issues

def find_list_formatting_issues(soup, text_content):
    """Find list formatting problems"""
    issues = []
    
    # Check HTML lists
    lists = soup.find_all(['ul', 'ol'])
    for list_elem in lists:
        items = list_elem.find_all('li')
        
        # Check for single-item lists
        if len(items) == 1:
            issues.append({
                "message": "Single-item list should be reformatted as regular text",
                "context": list_elem.get_text()[:100],
                "type": "single_item_list"
            })
        
        # Check for inconsistent list item formatting
        inconsistent_items = check_list_item_consistency(items)
        if inconsistent_items:
            issues.append({
                "message": "Inconsistent list item formatting (capitalization, punctuation)",
                "context": "; ".join([item[:30] for item in inconsistent_items]),
                "type": "inconsistent_formatting"
            })
    
    # Check for manual lists that should be formatted as proper lists
    manual_lists = find_manual_lists(text_content)
    for manual_list in manual_lists:
        issues.append({
            "message": "Manual list detected - should use proper list formatting",
            "context": manual_list[:100],
            "type": "manual_list"
        })
    
    return issues

def find_code_formatting_issues(soup, text_content):
    """Find code formatting problems"""
    issues = []
    
    # Check for inline code that should be code blocks
    inline_code_patterns = [
        r'`[^`\n]{50,}`',  # Very long inline code
        r'`[^`]*\n[^`]*`'   # Inline code with line breaks
    ]
    
    for pattern in inline_code_patterns:
        matches = re.finditer(pattern, text_content)
        for match in matches:
            issues.append({
                "message": "Long inline code should be formatted as code block",
                "context": match.group()[:100],
                "type": "inline_to_block"
            })
    
    # Check for unformatted code (common patterns)
    unformatted_code_patterns = [
        r'\b(function|class|def|var|let|const)\s+\w+',
        r'\w+\(\w*\)\s*{',
        r'if\s*\([^)]+\)\s*{',
        r'for\s*\([^)]+\)\s*{',
        r'import\s+\w+\s+from',
        r'<\w+[^>]*>'
    ]
    
    for pattern in unformatted_code_patterns:
        matches = re.finditer(pattern, text_content)
        for match in matches:
            # Check if it's not already in a code block/span
            if '`' not in text_content[max(0, match.start()-10):match.end()+10]:
                issues.append({
                    "message": "Code should be formatted with backticks or code blocks",
                    "context": match.group(),
                    "type": "unformatted_code"
                })
    
    return issues

def find_table_formatting_issues(soup):
    """Find table formatting problems"""
    issues = []
    
    tables = soup.find_all('table')
    for table in tables:
        # Check for missing headers
        if not table.find('th') and not table.find('thead'):
            issues.append({
                "message": "Table should have header row for accessibility",
                "context": str(table)[:100],
                "type": "missing_headers"
            })
        
        # Check for empty cells
        cells = table.find_all(['td', 'th'])
        empty_cells = [cell for cell in cells if not cell.get_text().strip()]
        if len(empty_cells) > len(cells) * 0.1:  # More than 10% empty
            issues.append({
                "message": f"Table has {len(empty_cells)} empty cells - consider table restructure",
                "context": str(table)[:100],
                "type": "many_empty_cells"
            })
    
    return issues

def find_paragraph_structure_issues(text_content):
    """Find paragraph structure problems"""
    issues = []
    
    paragraphs = text_content.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Check for very long paragraphs
        sentences = re.split(r'[.!?]+', paragraph)
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count > 8:
            issues.append({
                "message": f"Very long paragraph ({sentence_count} sentences) - consider breaking up",
                "context": paragraph[:100] + "...",
                "sentence_count": sentence_count,
                "type": "long_paragraph"
            })
        
        # Check for very short paragraphs (single sentence under 10 words)
        if sentence_count == 1 and len(paragraph.split()) < 10:
            issues.append({
                "message": "Very short paragraph - consider combining with adjacent paragraphs",
                "context": paragraph,
                "word_count": len(paragraph.split()),
                "type": "short_paragraph"
            })
    
    return issues

def find_whitespace_issues(text_content):
    """Find whitespace and spacing problems"""
    issues = []
    
    # Check for multiple spaces
    multiple_spaces = re.finditer(r' {2,}', text_content)
    for match in multiple_spaces:
        start = max(0, match.start() - 20)
        end = min(len(text_content), match.end() + 20)
        context = text_content[start:end]
        
        issues.append({
            "message": "Multiple consecutive spaces found",
            "context": context.strip(),
            "type": "multiple_spaces"
        })
    
    # Check for inconsistent line breaks
    inconsistent_breaks = re.finditer(r'\n{3,}', text_content)
    for match in inconsistent_breaks:
        issues.append({
            "message": "Excessive line breaks - use consistent paragraph spacing",
            "context": "Multiple blank lines",
            "type": "excessive_breaks"
        })
    
    # Check for trailing spaces
    trailing_spaces = re.finditer(r' +\n', text_content)
    for match in trailing_spaces:
        issues.append({
            "message": "Trailing spaces at end of line",
            "context": "Line ending with spaces",
            "type": "trailing_spaces"
        })
    
    return issues

def check_list_item_consistency(items):
    """Check if list items have consistent formatting"""
    inconsistent_items = []
    
    if len(items) < 2:
        return inconsistent_items
    
    # Check capitalization consistency
    first_chars = [item.get_text().strip()[0] if item.get_text().strip() else '' for item in items]
    first_chars = [char for char in first_chars if char]
    
    if len(set(char.isupper() for char in first_chars)) > 1:
        inconsistent_items.extend([item.get_text().strip() for item in items])
    
    return inconsistent_items

def find_manual_lists(text_content):
    """Find manually formatted lists that should use proper list formatting"""
    manual_lists = []
    
    # Look for patterns like:
    # - Item 1
    # - Item 2
    # or
    # 1. Item 1
    # 2. Item 2
    
    manual_list_patterns = [
        r'(?:^|\n)(?:[-*•]\s+.+(?:\n|$)){2,}',  # Bulleted lists
        r'(?:^|\n)(?:\d+\.\s+.+(?:\n|$)){2,}'   # Numbered lists
    ]
    
    for pattern in manual_list_patterns:
        matches = re.finditer(pattern, text_content, re.MULTILINE)
        for match in matches:
            manual_lists.append(match.group().strip())
    
    return manual_lists
