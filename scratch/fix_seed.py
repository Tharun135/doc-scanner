import os

file_path = 'scripts/seed_style_guide.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '"source": "Technical Style Guide"}',
    '"source": "Technical Style Guide", "source_type": "style_guide", "meta_source_type": "style_guide"}'
).replace(
    '"source": "Technical Branding"}',
    '"source": "Technical Branding", "source_type": "style_guide", "meta_source_type": "style_guide"}'
).replace(
    '"source": "Safety Policy"}',
    '"source": "Safety Policy", "source_type": "style_guide", "meta_source_type": "style_guide"}'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
