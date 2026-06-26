import json

file_path = 'scripts/seed_style_guide.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_rule = """    {
        "id": "sg-terminology-003",
        "text": (
            "Rule: Do not use 'on' after UI action verbs.\\n"
            "'Click on', 'tap on', and 'press on' are redundant constructions.\\n"
            "Bad:  'Click on the Save button.'\\n"
            "Good: 'Click the Save button.'\\n"
            "Bad:  'Double-click on the file.'\\n"
            "Good: 'Double-click the file.'"
        ),
        "metadata": {"category": "terminology", "severity": "medium", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },
"""

# Insert before the last rule
content = content.replace(
    '    # -----------------------------------------------------------------------',
    '    # -----------------------------------------------------------------------\n    # UI ACTIONS\n    # -----------------------------------------------------------------------\n' + new_rule + '\n    # -----------------------------------------------------------------------',
    1
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
