import os
import re

rules_dir = r"d:\doc-scanner\app\rules"
files = [f for f in os.listdir(rules_dir) if f.endswith('.py')]

for file in files:
    filepath = os.path.join(rules_dir, file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'import spacy' in content:
        new_content = content.replace('import spacy', '''try:
    import spacy
except ImportError:
    class DummySpacy:
        def load(self, *args, **kwargs):
            raise OSError("spacy not installed")
    spacy = DummySpacy()''')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched {file}")
