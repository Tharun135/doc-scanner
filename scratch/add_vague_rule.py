import json

file_path = 'scripts/seed_style_guide.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_rule = """    {
        "id": "sg-vague-001",
        "text": (
            "Rule: Avoid vague terms and ambiguous quantities like 'various', 'several', 'many', or 'some'.\\n"
            "Specify the exact amount or provide clear context.\\n"
            "Bad:  'It provides various editor functions.'\\n"
            "Good: 'It provides five editor functions: descriptions, categorization...'"
        ),
        "metadata": {"category": "clarity", "severity": "medium", "source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}
    },
"""

# Insert before the last rule
content = content.replace(
    '    # -----------------------------------------------------------------------',
    '    # -----------------------------------------------------------------------\n    # VAGUE TERMS\n    # -----------------------------------------------------------------------\n' + new_rule + '\n    # -----------------------------------------------------------------------',
    1
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
