"""
Formatting Rules - Compatible with App Structure
Detects formatting issues and returns position-based results.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def _check_space_before_punctuation(content: str) -> List[Dict[str, Any]]:
    """
    Check for spaces before punctuation, but allow them in list items.
    This function handles both full documents and individual sentences.
    """
    issues = []
    
    # If content is a single sentence without line breaks, check if it might be a list item
    if '\n' not in content.strip():
        # Single sentence - check if it looks like a list item content
        sentence = content.strip()
        
        # Skip flagging if sentence looks like list item content:
        # - Starts with typical list item text patterns
        # - Is short and descriptive (common in lists)
        # - Ends with space + punctuation (common list formatting)
        if (_looks_like_list_item(sentence)):
            return issues  # Don't flag list item sentences
    
    # Split content into lines to handle list detection
    lines = content.split('\n')
    current_pos = 0
    
    for line in lines:
        # Check if this line is a list item
        is_list_line = bool(re.match(r'^\s*[-*•·]\s', line) or re.match(r'^\s*\d+\.\s', line))
        
        if not is_list_line:
            # Only check for space before punctuation in non-list lines
            for match in re.finditer(r'\s+[.!?,:;]', line):
                matched_text = match.group(0)
                # Removed: Formatting issue: Remove space before punctuation
        
        # Move to next line (add 1 for the newline character)
        current_pos += len(line) + 1
    
    return issues

def _looks_like_list_item(sentence: str) -> bool:
    """
    Determine if a sentence looks like it could be a list item content.
    """
    sentence = sentence.strip()
    
    # Don't treat obviously conversational or narrative text as list items
    conversational_patterns = [
        r'^(I|You|We|They)\s+(think|believe|know|feel|said|told)',
        r'^(Hello|Hi|Hey)',
        r'^(This is wrong|That is incorrect|What\s*\?)',
        r'(everyone|somebody|anyone)\s+(left|came|went)',
        r'(meeting|party|event).*(ended|started|began)',
        r'^This\s+is\s+wrong',  # Specific pattern for error messages
    ]
    
    for pattern in conversational_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            return False
    
    # Check for common list item indicators
    list_indicators = [
        # Action words that start list items (fixed pattern to allow multiple words)
        r'^(The|A|An)\s+\w+(?:\s+\w+)*\s+(must|should|will|can|may|is|are)',
        r'^(Download|Install|Open|Close|Save|Create|Delete|Configure|Setup|Set up)',
        r'^(Click|Select|Choose|Enter|Type|Navigate|Browse|Search)',
        r'^(Ensure|Verify|Check|Confirm|Make sure)',
        r'^(Add|Remove|Edit|Modify|Update|Change)',
        
        # Descriptive patterns common in lists
        r'^(This|That|It)\s+(is|will|should|must|can|may)\s+(required|needed|necessary)',
        r'^(First|Second|Third|Next|Then|Finally|Last)',
        r'^(Required|Optional|Important|Note|Warning)',
        
        # Technical documentation patterns (fixed to allow multiple words)
        r'^(The\s+\w+(?:\s+\w+)*\s+(application|app|system|software|program|tool))',
        r'^(A\s+(project|file|document|configuration|setting))',
    ]
    
    # Check if sentence matches any list item pattern
    for pattern in list_indicators:
        if re.match(pattern, sentence, re.IGNORECASE):
            return True
    
    # Check if sentence has space before punctuation at the end (common list formatting)
    if re.search(r'\s+[.!?]$', sentence):
        # Additional checks to confirm it's likely a list item
        word_count = len(sentence.split())
        
        # Only allow for short, descriptive sentences (3-12 words)
        if 3 <= word_count <= 12:
            # Must start with technical/instructional words
            if re.match(r'^(The|A|An|Download|Install|Open|Close|Save|Create|Configure|Setup)', sentence, re.IGNORECASE):
                return True
        
        # Longer sentences that clearly match list patterns
        if word_count > 12 and any(re.match(pattern, sentence, re.IGNORECASE) for pattern in list_indicators[:5]):
            return True
    
    return False

def check(content: str) -> List[Dict[str, Any]]:
    """
    Check for formatting issues with position information.
    Returns a list of dictionaries with text positions for app compatibility.
    """
    issues = []
    
    # Handle space before punctuation with list awareness
    issues.extend(_check_space_before_punctuation(content))
    
    # Define other formatting patterns (excluding space before punctuation)
    formatting_patterns = [
        # Multiple spaces
        {
            'pattern': r'[^\s]\s{2,}[^\s]',
            'flags': 0,
            'message': 'Formatting issue: Multiple consecutive spaces detected'
        },
        # Inconsistent quote usage
        {
            'pattern': r'["]{3}.*?["]{3}',
            'flags': 0,
            'message': 'Formatting issue: Use consistent quotation marks (straight quotes recommended)'
        },
    # Removed: Formatting issue: Add space after punctuation
    # Removed: Formatting issue: Add space after comma
        # Inconsistent bullet points
        {
            'pattern': r'^[\s]*[-*•·]\s*[a-zA-Z]',
            'flags': re.MULTILINE,
            'message': 'Formatting issue: Use consistent bullet point style'
        },
    # Removed: Formatting issue: Add spaces around operators
        # Inconsistent dash usage
        {
            'pattern': r'[a-zA-Z]-[a-zA-Z]',
            'flags': 0,
            'message': 'Formatting issue: Check hyphen usage in compound words'
        },
        # Multiple line breaks
        {
            'pattern': r'\n\s*\n\s*\n',
            'flags': 0,
            'message': 'Formatting issue: Excessive line breaks detected'
        },
        # Trailing whitespace
        {
            'pattern': r'[^\s]\s+$',
            'flags': re.MULTILINE,
            'message': 'Formatting issue: Trailing whitespace at end of line'
        }
    ]

    # Only check inconsistent capitalization in actual headings (Markdown or HTML)
    # Markdown headings: lines starting with #
    heading_pattern = re.compile(r'^(#+)\s+(.*)$', re.MULTILINE)
    for match in heading_pattern.finditer(content):
        heading_text = match.group(2).strip()
        # If heading contains both lowercase and uppercase words, flag it
        if re.search(r'[A-Z][a-z]+\s+[a-z]+\s+[A-Z]', heading_text):
            issues.append({
                "text": heading_text,
                "start": match.start(2),
                "end": match.end(2),
                "message": "Formatting issue: Inconsistent capitalization in heading"
            })

    # HTML headings: <h1>...</h1> etc.
    html_heading_pattern = re.compile(r'<h[1-6][^>]*>(.*?)</h[1-6]>', re.IGNORECASE)
    for match in html_heading_pattern.finditer(content):
        heading_text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        if re.search(r'[A-Z][a-z]+\s+[a-z]+\s+[A-Z]', heading_text):
            issues.append({
                "text": heading_text,
                "start": match.start(1),
                "end": match.end(1),
                "message": "Formatting issue: Inconsistent capitalization in heading"
            })

    # Collect heading ranges so we can skip some formatting checks inside titles
    heading_ranges = []
    for m in heading_pattern.finditer(content):
        heading_ranges.append((m.start(2), m.end(2)))
    for m in html_heading_pattern.finditer(content):
        heading_ranges.append((m.start(1), m.end(1)))

    # Also treat a short first line (common title without markup) as a heading/title
    # Criteria: first non-empty line, short number of words, not a markdown/HTML heading, and not a code block marker
    first_line_match = re.search(r'^(.*)$', content, re.MULTILINE)
    if first_line_match:
        first_line = first_line_match.group(1).strip()
        if first_line:
            word_count = len(first_line.split())
            char_count = len(first_line)
            # Heuristic: consider it a title if <= 8 words and <= 60 chars
            if word_count <= 8 and char_count <= 60:
                # Skip if it already looks like a markdown heading or an HTML tag
                if not re.match(r'^#{1,6}\s', first_line) and not first_line.startswith('<') and not first_line.startswith('```'):
                    fl_start = first_line_match.start(1)
                    fl_end = first_line_match.end(1)
                    heading_ranges.append((fl_start, fl_end))

    # Build sentence spans to identify which sentence a match belongs to
    sentence_spans = []
    for m in re.finditer(r'[^.!?]+[.!?]?|\n+', content, re.DOTALL):
        # normalize spans: skip pure whitespace spans
        span_text = m.group(0)
        if span_text.strip() == '':
            continue
        sentence_spans.append((m.start(), m.end()))

    seen = set()  # store tuples of (message, sentence_index) to avoid duplicates per sentence

    for pattern_info in formatting_patterns:
        pattern = pattern_info['pattern']
        flags = pattern_info.get('flags', 0)
        message = pattern_info['message']
        
        for match in re.finditer(pattern, content, flags):
            matched_text = match.group(0)

            # Do not apply the large-number comma suggestion inside headings/titles
            if 'comma separators' in message:
                in_heading = any(start <= match.start() < end for (start, end) in heading_ranges)
                if in_heading:
                    continue

            # Determine which sentence span this match belongs to
            sentence_index = None
            for idx, (s_start, s_end) in enumerate(sentence_spans):
                if s_start <= match.start() < s_end:
                    sentence_index = idx
                    break

            # If we couldn't map to a sentence, allow the issue (use -1 as bucket)
            key = (message, sentence_index if sentence_index is not None else -1)
            if key in seen:
                # Duplicate issue of same message in same sentence — skip
                continue

            seen.add(key)

            issues.append({
                "text": matched_text,
                "start": match.start(),
                "end": match.end(),
                "message": message
            })

    return issues
