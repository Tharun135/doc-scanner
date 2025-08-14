"""
New Streamlined Rules System
Only 8 consolidated rule categories with AI-powered suggestions.
"""

# Import all new rule categories
from app.rules.grammar import check as check_grammar
from app.rules.clarity import check as check_clarity
from app.rules.formatting import check as check_formatting
from app.rules.tone import check as check_tone
from app.rules.terminology import check as check_terminology
from app.rules.accessibility import check as check_accessibility
from app.rules.punctuation import check as check_punctuation
from app.rules.capitalization import check as check_capitalization

# List of all new rule functions
rule_functions = [
    check_grammar,           # Grammar & Syntax (15 rules)
    check_clarity,           # Clarity & Conciseness (15 rules)
    check_formatting,        # Formatting & Structure (15 rules)
    check_tone,              # Tone & Voice (10 rules)
    check_terminology,       # Terminology (10 rules)
    check_accessibility,     # Accessibility & Inclusivity (10 rules)
    check_punctuation,       # Punctuation (15 rules)
    check_capitalization,    # Capitalization (10 rules)
]

# Total: 100 consolidated rules across 8 categories
