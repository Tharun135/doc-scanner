"""
Punctuation Rules Checker
========================

Implements comprehensive punctuation rules based on reference files:
- Oxford comma usage
- Proper period placement  
- Quotation mark consistency
- Hyphen vs en-dash vs em-dash usage
- Exclamation point overuse
- Apostrophe usage
- Colon and semicolon usage
- Parentheses and brackets usage
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
    """Main punctuation checker function."""
    suggestions = []

    # Strip HTML tags from content but preserve structure info
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "punctuation",
            "Check for punctuation issues including Oxford comma, period placement, quotation marks, dash usage, and exclamation point overuse."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    suggestions.extend(check_oxford_comma(text_content))
    suggestions.extend(check_period_placement(text_content))
    suggestions.extend(check_exclamation_overuse(text_content))
    suggestions.extend(check_quotation_marks(text_content))
    suggestions.extend(check_dash_usage(text_content))
    suggestions.extend(check_apostrophe_usage(text_content))
    suggestions.extend(check_colon_semicolon_usage(text_content))

    return suggestions if suggestions else []

def check_oxford_comma(text_content):
    """Check for missing Oxford comma in lists of three or more items."""
    suggestions = []
    
    # Pattern to find lists with 'and' or 'or' without Oxford comma
    # Example: "red, blue and green" should be "red, blue, and green"
    oxford_pattern = r'\b(\w+),\s+(\w+)\s+(and|or)\s+(\w+)\b'
    
    matches = re.finditer(oxford_pattern, text_content, re.IGNORECASE)
    
    for match in matches:
        full_match = match.group(0)
        item1, item2, conjunction, item3 = match.groups()
        
        # Skip if it's already correct (has comma before conjunction)
        if f', {conjunction}' in full_match:
            continue
            
        # Skip common exceptions (names, titles, etc.)
        exceptions = [
            'black and white',
            'salt and pepper', 
            'bread and butter',
            'rock and roll',
            'trial and error'
        ]
        
        if any(exception in full_match.lower() for exception in exceptions):
            continue
            
        start_pos = match.start()
        end_pos = match.end()
        
        corrected = f"{item1}, {item2}, {conjunction} {item3}"
        
        suggestions.append({
            "text": full_match,
            "start": start_pos,
            "end": end_pos,
            "message": f"Consider adding Oxford comma: '{full_match}' → '{corrected}'"
        })
    
    return suggestions

def check_period_placement(text_content):
    """Check for missing periods at the end of sentences."""
    suggestions = []
    
    # Split into lines and check each line
    lines = text_content.split('\n')
    
    current_position = 0  # Track position in the full document
    
    for line_num, line in enumerate(lines):
        line_start_position = current_position
        line = line.strip()
        original_line = lines[line_num]  # Keep original with whitespace for position calculation
        
        # Update position for next iteration (include the newline character)
        current_position += len(original_line) + 1  # +1 for the \n character
        
        # Skip empty lines, headers, list items, and short phrases
        if (not line or 
            len(line) < 10 or
            line.startswith(('#', '*', '-', '•', '1.', '2.', '3.', '4.', '5.')) or
            line.isupper() or  # Skip headings in all caps
            ':' in line and len(line) < 50):  # Skip labels/captions
            continue
            
        # Check if line looks like a complete sentence but missing period
        if (len(line.split()) >= 5 and  # At least 5 words
            not line.endswith(('.', '!', '?', ':', ';', '"', "'", ')', ']', '}')) and
            not line.endswith('...') and
            re.search(r'\b(the|a|an|is|are|was|were|have|has|will|can|should|would)\b', line.lower())):
            
            # Find the actual position of this line in the full document
            line_position_in_document = text_content.find(line, line_start_position)
            if line_position_in_document == -1:
                # Fallback: try to find the line without position constraint
                line_position_in_document = text_content.find(line)
            
            if line_position_in_document != -1:
                suggestions.append({
                    "text": line,
                    "start": line_position_in_document,
                    "end": line_position_in_document + len(line),
                    "message": f"Consider adding period at end of sentence: '{line}'"
                })
            else:
                # Last resort: use approximate position (this shouldn't happen often)
                suggestions.append({
                    "text": line,
                    "start": line_start_position,
                    "end": line_start_position + len(line),
                    "message": f"Consider adding period at end of sentence: '{line}'"
                })
    
    return suggestions

def check_exclamation_overuse(text_content):
    """Check for excessive use of exclamation points."""
    suggestions = []
    
    # Count exclamation points in text
    exclamation_count = text_content.count('!')
    total_sentences = len(re.findall(r'[.!?]+', text_content))
    
    if total_sentences > 0:
        exclamation_ratio = exclamation_count / total_sentences
        
        # Flag if more than 10% of sentences use exclamation points
        if exclamation_ratio > 0.1 and exclamation_count > 2:
            # Find the first exclamation point for positioning
            first_exclamation = text_content.find('!')
            if first_exclamation == -1:
                first_exclamation = 0  # Fallback
                
            suggestions.append({
                "text": "!",
                "start": first_exclamation,  # FIXED: Use position of first exclamation
                "end": first_exclamation + 1,
                "message": f"Excessive exclamation point usage: {exclamation_count} exclamation points in {total_sentences} sentences. Consider using periods for most statements."
            })
    
    # Check for multiple consecutive exclamation points
    multiple_exclamation = re.finditer(r'!{2,}', text_content)
    
    for match in multiple_exclamation:
        suggestions.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "message": f"Use single exclamation point instead of multiple: '{match.group(0)}' → '!'"
        })
    
    return suggestions

def check_quotation_marks(text_content):
    """Check for quotation mark consistency and proper usage."""
    import re
    suggestions = []
    
    # IMPROVED: Distinguish between apostrophes and actual single quotation marks
    # Count only single quotes that are likely to be quotation marks, not apostrophes
    
    # Find actual single quotation marks (not apostrophes)
    # Apostrophes are typically within words (contractions) or possessives
    # Quotation marks are typically at word boundaries
    
    # Pattern to find apostrophes (contractions and possessives)
    apostrophe_pattern = r"[a-zA-Z]'[a-zA-Z]|[a-zA-Z]'s\b|[a-zA-Z]'t\b|[a-zA-Z]'re\b|[a-zA-Z]'ve\b|[a-zA-Z]'ll\b|[a-zA-Z]'d\b|[a-zA-Z]'m\b"
    apostrophes = len(re.findall(apostrophe_pattern, text_content))
    
    # Count all single quotes
    total_single_quotes = text_content.count("'")
    
    # Actual quotation marks = total single quotes - apostrophes
    quotation_single_quotes = total_single_quotes - apostrophes
    
    # Check for double quotes (these are always quotation marks)
    double_quotes = text_content.count('"')
    
    # Check for uneven quote counts (potential mismatch) - only for actual quotation marks
    if quotation_single_quotes > 0 and quotation_single_quotes % 2 != 0:
        # Find the first single quote that's not an apostrophe
        first_quote_pos = 0
        for match in re.finditer(r"'", text_content):
            pos = match.start()
            # Check if this is likely an apostrophe
            if pos > 0 and pos < len(text_content) - 1:
                before_char = text_content[pos - 1]
                after_char = text_content[pos + 1]
                # Skip if it looks like an apostrophe (letter before and after, or possessive/contraction)
                if (before_char.isalpha() and after_char.isalpha()) or \
                   (before_char.isalpha() and after_char in 's') or \
                   (before_char.isalpha() and text_content[pos:pos+3] in ["'t ", "'re", "'ve", "'ll", "'d ", "'m "]):
                    continue
            # This looks like a quotation mark
            first_quote_pos = pos
            break
            
        if first_quote_pos > 0:
            suggestions.append({
                "text": "'",
                "start": first_quote_pos,
                "end": first_quote_pos + 1,
                "message": f"Unmatched single quotation marks detected. Found {quotation_single_quotes} quotation marks - should be even number. (Apostrophes in contractions like \"don't\" are not counted)"
            })
    
    if double_quotes % 2 != 0:
        # Find the first double quote for positioning
        first_double_quote = text_content.find('"')
        if first_double_quote == -1:
            first_double_quote = 0  # Fallback
            
        suggestions.append({
            "text": '"',
            "start": first_double_quote,  # FIXED: Use position of first double quote
            "end": first_double_quote + 1,
            "message": f"Unmatched double quotation marks detected. Found {double_quotes} double quotes - should be even number."
        })
    
    # Check for incorrect quotation mark placement with punctuation
    # Incorrect: "Hello", she said. Correct: "Hello," she said.
    incorrect_quote_punct = re.finditer(r'"\s*[,.]', text_content)
    
    for match in incorrect_quote_punct:
        suggestions.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "message": f"Move punctuation inside quotation marks: '{match.group(0).strip()}' → '\"[punctuation]'"
        })
    
    return suggestions

def check_dash_usage(text_content):
    """Check for proper hyphen, en-dash, and em-dash usage."""
    import re
    suggestions = []
    
    # Check for double hyphens that should be em-dashes
    # BUT exclude markdown syntax contexts
    double_hyphen = re.finditer(r'--+', text_content)
    
    for match in double_hyphen:
        # Get the context around the match
        start_pos = match.start()
        end_pos = match.end()
        
        # Find the line containing this match
        line_start = text_content.rfind('\n', 0, start_pos) + 1
        line_end = text_content.find('\n', end_pos)
        if line_end == -1:
            line_end = len(text_content)
        
        current_line = text_content[line_start:line_end]
        
        # Skip if this looks like markdown table syntax
        # Markdown tables use | and --- patterns
        if '|' in current_line and re.search(r'^\s*\|?[\s\-\|:]+\|?\s*$', current_line.strip()):
            continue
            
        # Skip if this is a markdown horizontal rule (--- on its own line)
        if re.match(r'^\s*-{3,}\s*$', current_line.strip()):
            continue
            
        # Skip if this is part of a YAML front matter or similar (--- at start of line)
        if re.match(r'^\s*-{3,}', current_line.strip()):
            continue
            
        # Skip if this appears to be a code block or technical content
        # Look for surrounding context that suggests technical usage
        context_before = text_content[max(0, start_pos - 50):start_pos]
        context_after = text_content[end_pos:min(len(text_content), end_pos + 50)]
        
        # Skip if surrounded by code-like characters
        if any(char in context_before + context_after for char in ['`', '{', '}', '<', '>', '=', 'http']):
            continue
        
        # If we get here, it's likely a genuine case where em-dash should be used
        suggestions.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "message": f"Use em-dash instead of double hyphen: '{match.group(0)}' → '—'"
        })
    
    # Check for spaced hyphens that should be em-dashes
    spaced_hyphen = re.finditer(r'\s+-\s+', text_content)
    
    for match in spaced_hyphen:
        # Skip if it's a bullet point or list item
        line_start = text_content.rfind('\n', 0, match.start()) + 1
        line_part = text_content[line_start:match.start()].strip()
        
        if not line_part:  # Beginning of line - likely a bullet point
            continue
            
        suggestions.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "message": f"Use em-dash for parenthetical expressions: '{match.group(0)}' → '—'"
        })
    
    return suggestions

def check_apostrophe_usage(text_content):
    """Check for common apostrophe errors."""
    suggestions = []
    
    # Check for incorrect possessive forms
    incorrect_possessives = [
        (r"\bit's\b(?!\s+(a|an|the|been|going|time|important))", "Use 'its' for possessive, 'it's' only for 'it is' or 'it has'"),
        (r"\byou're\s+(?:house|car|book|idea|problem)", "Use 'your' for possessive, 'you're' only for 'you are'"),
        (r"\btheir\s+(?:going|coming|not)", "Use 'they're' for 'they are', 'their' for possessive"),
        (r"\bwhos\s+(?:house|car|book)", "Use 'whose' for possessive, 'who's' only for 'who is'")
    ]
    
    for pattern, message in incorrect_possessives:
        matches = re.finditer(pattern, text_content, re.IGNORECASE)
        
        for match in matches:
            suggestions.append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "message": message
            })
    
    return suggestions

def check_colon_semicolon_usage(text_content):
    """Check for proper colon and semicolon usage."""
    suggestions = []
    
    # Check for semicolons in simple lists (should use commas)
    semicolon_in_simple_list = re.finditer(r'\b\w+;\s*\w+;\s*\w+\b', text_content)
    
    for match in semicolon_in_simple_list:
        # Check if items are simple (no internal commas)
        list_part = match.group(0)
        if list_part.count(',') == 0:  # No internal commas, should use commas instead
            suggestions.append({
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "message": f"Use commas for simple lists: '{match.group(0)}' (semicolons are for complex lists with internal commas)"
            })
    
    # Check for colons not followed by list or explanation
    incorrect_colon = re.finditer(r':\s*[a-z]', text_content)
    
    for match in incorrect_colon:
        # Skip if it's a time format (like 12:30)
        if re.search(r'\d+:\d+', match.group(0)):
            continue
            
        suggestions.append({
            "text": match.group(0),
            "start": match.start(),
            "end": match.end(),
            "message": "Capitalize first word after colon if it begins a complete sentence"
        })
    
    return suggestions

if __name__ == "__main__":
    # Test the punctuation rules
    test_content = """
    <p>I like red, blue and green colors. This sentence is missing a period</p>
    <p>This is amazing!!! I can't believe it!</p>
    <p>"Hello", she said. The quote punctuation is wrong.</p>
    <p>This is a test -- with double hyphens.</p>
    <p>Its a beautiful day. You're house is nice.</p>
    """
    
    print("🔍 Testing Punctuation Rules")
    print("=" * 40)
    
    results = check(test_content)
    
    for i, suggestion in enumerate(results, 1):
        print(f"{i}. {suggestion.get('message', 'No message')}")
        if suggestion.get('text'):
            print(f"   Text: '{suggestion['text']}'")
    
    if not results:
        print("No punctuation issues found!")
