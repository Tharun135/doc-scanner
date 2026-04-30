"""
Centralized configuration for documentation rules.
"""

# Sections where certain rules are exempted to avoid false positives based on document context.
# All section names should be lowercase for case-insensitive matching.
SECTION_EXEMPTIONS = {
    "passive_voice": [
        "prerequisites", 
        "system requirements", 
        "notes", 
        "overview", 
        "about", 
        "background", 
        "introduction"
    ],
    "imperative_mood": [
        "overview", 
        "description", 
        "background"
    ],
}
