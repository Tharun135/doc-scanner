import re
import spacy
from bs4 import BeautifulSoup

# Import RAG system with fallback
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
        nlp.max_length = 3000000  # Increase max length to 3MB
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

    # Extract plain text (remove HTML if present)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    
    try:
        nlp_model = _get_nlp()
        doc = nlp_model(text_content)
    except Exception as e:
        doc = None

    # ------------------------------
    # Regex-based style checks
    # ------------------------------
    # Check for passive voice using "by" + past participle
    if re.search(r"\bby\s+\w+ed\b", text_content, flags=re.IGNORECASE):
        suggestions.append("Consider avoiding passive voice where possible.")

    # Multiple exclamation marks check removed per user request
    # if re.search(r"!{2,}", text_content):
    #     suggestions.append("Avoid using multiple exclamation marks.")

    # ALL CAPS check removed per user request

    # ------------------------------
    # spaCy-based style checks
    # ------------------------------
    if doc is not None:
        for sent in doc.sents:
            # Skip titles and headings for style checks
            if TITLE_UTILS_AVAILABLE and is_title_or_heading(sent.text.strip(), content):
                continue
            
            # Skip code blocks and diagrams
            if is_code_or_diagram(sent.text.strip()):
                continue
            
            # ============================================================
            # ADVERB DETECTION WITH CONTEXT ANALYSIS
            # ============================================================
            
            # Subjective/technical adverbs that may be intentional
            subjective_adverbs = {
                'properly', 'correctly', 'appropriately', 'specifically', 
                'exactly', 'directly', 'explicitly', 'clearly', 'successfully'
            }
            
            for token in sent:
                if token.text.endswith("ly") and token.pos_ == "ADV":
                    adverb_lower = token.text.lower()
                    
                    if adverb_lower in subjective_adverbs:
                        # DECISION: no_change - Technical/domain-specific term
                        suggestions.append({
                            'text': sent.text.strip(),
                            'start': 0,
                            'end': len(sent.text.strip()),
                            'message': f"Adverb '{token.text}' detected",
                            'decision_type': 'no_change',
                            'rule': 'style_adverbs',
                            'reviewer_rationale': f"'{token.text}' may be intentional and domain-specific. In technical contexts, terms like 'properly configured' or 'correctly installed' convey specific technical meaning that would be lost if removed. Consider whether this adverb clarifies a technical requirement."
                        })
                    else:
                        # DECISION: guide - Suggest consideration
                        suggestions.append({
                            'text': sent.text.strip(),
                            'start': 0,
                            'end': len(sent.text.strip()),
                            'message': f"Adverb '{token.text}' detected",
                            'decision_type': 'guide',
                            'rule': 'style_adverbs',
                            'reviewer_rationale': f"Consider if '{token.text}' adds value. Adverbs ending in -ly can often be removed or replaced with more specific verbs for stronger, more direct writing. For example: 'quickly run' → 'sprint', 'carefully check' → 'verify'."
                        })

            # ============================================================
            # "VERY" DETECTION
            # ============================================================
            if "very" in sent.text.lower():
                # DECISION: guide - Generic intensifier
                suggestions.append({
                    'text': sent.text.strip(),
                    'start': 0,
                    'end': len(sent.text.strip()),
                    'message': "'very' detected",
                    'decision_type': 'guide',
                    'rule': 'style_intensifier',
                    'reviewer_rationale': "Consider replacing 'very' with more specific descriptive words. Examples: 'very big' → 'huge', 'very small' → 'tiny', 'very important' → 'critical'. This makes writing more precise and impactful."
                })

    # ------------------------------
    # RAG-based contextual style checks (if available)
    # ------------------------------
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(text_content, rule_type="style")
        suggestions.extend(rag_suggestions)

    return suggestions
