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

def is_code_or_diagram(text: str) -> bool:
    """Detect code blocks, diagrams, and technical syntax that shouldn't be analyzed."""
    text = text.strip().lower()
    if not text:
        return True
    
    # Code/diagram markers
    code_markers = ['mermaid', 'flowchart', 'sequencediagram', 'graph', 'json', 'yaml', 'xml', 'html', '```', '{', '[', '<', '-->', '|', '---', ':::', '~~~']
    if any(text.startswith(marker) for marker in code_markers):
        return True
    
    # High syntax density (>20% special chars = likely code)
    syntax_chars = sum(1 for c in text if c in '{}[]()<>|→-=:')
    if len(text) > 10 and syntax_chars / len(text) > 0.2:
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
        
        # Skip code blocks and diagrams
        if is_code_or_diagram(sent.text.strip()):
            continue
            
        # Skip markdown table separator rows (| --- | --- | etc.)
        sent_text = sent.text.strip()
        if re.match(r'^\|\s*---.*\|\s*$', sent_text) or '| --- |' in sent_text:
            continue
            
        # Skip markdown table rows (containing multiple | characters)
        if sent_text.count('|') >= 3 and ('| --- |' in sent_text or re.match(r'^\|.*\|.*\|', sent_text)):
            continue
            
        if len(sent) > 25:
            word_count = len(sent)
            
            # ============================================================
            # CONTEXT ANALYSIS: Determine if sentence should be split
            # ============================================================
            
            # Check for compliance/conditional markers
            compliance_markers = ['must', 'shall', 'required', 'necessary']
            conditional_markers = [' if ', ' unless ', ' provided that ', ' when ', ' in case ']
            
            sent_lower = sent_text.lower()
            
            # Count compliance markers
            compliance_count = sum(1 for marker in compliance_markers if marker in sent_lower)
            
            # Count significant conditional markers (not simple sequence words)
            conditional_count = sum(1 for marker in conditional_markers if marker in sent_lower)
            
            # Check for "or" indicating alternatives in compliance context
            has_alternatives = ' or ' in sent_lower and compliance_count > 0
            
            # Determine if this is a complex compliance/conditional sentence
            # Requires: compliance word + multiple conditions or conditions + alternatives
            is_compliance_conditional = (
                compliance_count >= 1 and 
                (conditional_count >= 2 or (conditional_count >= 1 and has_alternatives))
            )
            
            # ============================================================
            # DECISION LOGIC: Split vs. Explain
            # ============================================================
            
            if is_compliance_conditional:
                # DECISION: explain - Complex requirement, don't split
                suggestions.append({
                    'text': sent_text,
                    'start': 0,
                    'end': len(sent_text),
                    'message': f'Long conditional/compliance sentence detected ({word_count} words)',
                    'decision_type': 'explain',
                    'rule': 'long_sentence',
                    'reviewer_rationale': 'This sentence defines a complex requirement with multiple conditions and alternatives. Splitting it could separate logically connected requirements and reduce clarity. The length is justified by the semantic complexity - the conditions form a single logical unit.',
                    'explanation': 'Compliance and conditional sentences often need multiple clauses to express requirements accurately. Before splitting, verify that each condition would remain clear if separated. Consider if bullet points or a table might clarify the alternatives without breaking the logical relationship.'
                })
            else:
                # DECISION: rewrite - Simple long sentence, can be split
                suggestions.append({
                    'text': sent_text,
                    'start': 0,
                    'end': len(sent_text),
                    'message': f'Long sentence detected ({word_count} words)',
                    'decision_type': 'rewrite',
                    'rule': 'long_sentence',
                    'reviewer_rationale': f'Long sentences ({word_count} words) reduce readability. Breaking into 2-3 focused sentences improves clarity and makes information easier to process. Each sentence should focus on one main idea.',
                    'ai_suggestion': None  # Will be filled by enrichment service
                })
    
    return suggestions
