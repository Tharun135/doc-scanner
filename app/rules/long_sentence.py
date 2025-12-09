import re
import spacy
from bs4 import BeautifulSoup
import html

try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

try:
    from .title_utils import is_title_or_heading
    TITLE_UTILS_AVAILABLE = True
except ImportError:
    TITLE_UTILS_AVAILABLE = False

# Load spaCy model lazily to avoid startup issues
nlp = None

def _get_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")
        nlp.max_length = 3000000  # Increase max_length to handle large documents
    return nlp

def _is_table_row(text):
    """
    Detect if a text string is a markdown table row.
    
    Table rows have these characteristics:
    - Multiple pipe (|) characters (at least 3)
    - Content between pipes is usually short (cell data)
    - Often contains numbers, percentages, or short phrases
    - May start and end with pipes
    
    Examples:
    - "| 150K | 286.6 (57.32%) | Integrated with backend | 30670 |"
    - "| Name | Age | City |"
    - "| --- | --- | --- |"
    """
    if not text:
        return False
    
    # Must have at least 3 pipe characters (minimum 2 cells)
    pipe_count = text.count('|')
    if pipe_count < 3:
        return False
    
    # Check for separator row pattern (| --- | --- |)
    if re.match(r'^\|\s*[-:]+\s*\|', text):
        return True
    
    # Check if it looks like a table row:
    # 1. Starts and/or ends with pipe
    # 2. Has multiple pipes throughout
    # 3. Content between pipes is short (typical cell content)
    if text.startswith('|') or text.endswith('|'):
        # Split by pipes and check if cells look like table data
        cells = [cell.strip() for cell in text.split('|') if cell.strip()]
        
        # Table rows typically have 2+ cells
        if len(cells) >= 2:
            # Check if cells are relatively short (typical table cell length)
            # Normal sentences in table cells are usually < 15 words
            avg_cell_length = sum(len(cell.split()) for cell in cells) / len(cells)
            
            # If average cell length is short, it's likely a table
            if avg_cell_length < 15:
                return True
            
            # Even with longer cells, if we have many pipes and short cells mixed, it's a table
            short_cells = sum(1 for cell in cells if len(cell.split()) < 10)
            if short_cells >= len(cells) * 0.6:  # 60% of cells are short
                return True
    
    return False

def check(content):
    suggestions = []
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    try:
        nlp_model = _get_nlp()
        doc = nlp_model(text_content)
    except Exception as e:
        return []  # Return empty if spaCy fails

    # Flag long sentences (>25 words) - exclude titles and markdown tables
    for sent in doc.sents:
        # Skip if this appears to be a title or heading
        if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
            continue
            
        sent_text = sent.text.strip()
        
        # Skip markdown table separator rows (| --- | --- | etc.)
        if re.match(r'^\|\s*---.*\|\s*$', sent_text) or '| --- |' in sent_text:
            continue
        
        # Skip markdown table rows - enhanced detection
        # Tables have multiple pipe characters and typically contain cells
        if _is_table_row(sent_text):
            continue
            
        if len(sent) > 25:
            # Don't include the sentence text - the UI already shows which sentence has the issue
            word_count = len(sent)
            suggestions.append(f"Consider breaking this long sentence ({word_count} words) into shorter ones for better readability")
    
    return suggestions
