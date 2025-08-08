import re
from .spacy_utils import get_nlp_model
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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = get_nlp_model()

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    """
    Checks for correct references to Cascading Style Sheets (CSS):
      1. Capitalize references to the technique (Cascading Style Sheets).
      2. Spell out 'Cascading Style Sheets' unless audience is known to be familiar with 'CSS'.
      3. Lowercase references to style sheets created using the technique.
      4. Don't use 'CSS' to refer to a specific style sheet file => use 'the CSS file' or 'the style sheet' instead.
    """

    # 1. Check if "cascading style sheets" is capitalized properly.
    # We'll use a pattern to detect phrases that should be "Cascading Style Sheets."
    # If user wrote "cascading style sheets," we remind them to capitalize it.
    css_technique_pattern = r'\bcascading\s+style\s+sheets\b'
    matches = re.finditer(css_technique_pattern, content, flags=re.IGNORECASE)
    for match in matches:
 #       line_number = get_line_number(content, match.start())
        # We'll suggest capitalizing it
        suggestions.append("Capitalize references to the technique as 'Cascading Style Sheets'."
        )

    # 2. Lowercase references to style sheets if they appear capitalized as "Style Sheet" or "Style Sheets"
    #    We only want to enforce e.g. "Use a custom style sheet," not "Use a custom Style Sheet."
    style_sheet_pattern = r'\b[Ss]tyle\s+[Ss]heet(s)?\b'
    for match in re.finditer(style_sheet_pattern, content):
        matched_text = match.group()
#        line_number = get_line_number(content, match.start())
        # If the matched phrase is not all lowercase
        if matched_text != matched_text.lower():
            # Suggest using "style sheet" or "style sheets"
            suggestions.append("Lowercase references to style sheets when referring to actual files. "
                f"Use '{matched_text.lower()}' instead of '{matched_text}'."
            )

    # 3. Don't use "CSS" to refer to a specific style sheet
    #    We'll detect patterns like "the CSS" or "this CSS" or "my CSS" if it precedes "file" or "sheet"
    #    Then we suggest "the CSS file," "the style sheet," or "the cascading style sheet."
    #    This is heuristic-based but helps guide usage.
    specific_css_pattern = r'\bcss\s+(file|sheet)\b'
    for match in re.finditer(specific_css_pattern, content, flags=re.IGNORECASE):
#        line_number = get_line_number(content, match.start())
        suggestions.append("Don't use 'CSS' to refer to a specific style sheet. "
            "Use 'the CSS file', 'the cascading style sheet', or 'the style sheet' instead."
        )

    # Additional logic:
    # If you want to catch usage of "CSS" alone for a file, e.g. "there is a problem with the CSS" => 
    # we can detect that pattern if it is followed by context or if doc can parse the mention.
    # For example:
    standalone_css_pattern = r'\bthe\s+css\b'
    for match in re.finditer(standalone_css_pattern, content, flags=re.IGNORECASE):
#        line_number = get_line_number(content, match.start())
        suggestions.append("Avoid using 'the CSS' if referring to a specific file. "
            "Use 'the CSS file' or 'the style sheet'."
        )
    return suggestions if suggestions else []