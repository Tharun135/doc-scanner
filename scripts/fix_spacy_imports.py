"""
Automated Fix - Replace all spaCy imports with shared utility
"""

import os
import re

def fix_spacy_imports():
    """Replace all individual spaCy imports with shared utility."""
    print("🔧 AUTOMATED SPACY IMPORT FIX")
    print("=" * 50)
    
    rules_dir = os.path.join(os.path.dirname(__file__), 'app', 'rules')
    rules_fixed = 0
    rules_skipped = 0
    
    # Get all Python files in rules directory
    for filename in os.listdir(rules_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'spacy_utils.py', 'technical_terms_clean.py']:
            file_path = os.path.join(rules_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has spaCy import
                if 'import spacy' in content:
                    print(f"🔧 Fixing {filename}...")
                    
                    # Replace spaCy imports with shared utility
                    new_content = content.replace(
                        'import spacy',
                        'from .spacy_utils import get_nlp_model'
                    )
                    
                    # Replace spacy.load calls with shared utility
                    new_content = re.sub(
                        r'spacy\.load\([^)]+\)',
                        'get_nlp_model()',
                        new_content
                    )
                    
                    # Replace nlp = spacy.load(...) with nlp = get_nlp_model()
                    new_content = re.sub(
                        r'nlp\s*=\s*spacy\.load\([^)]+\)',
                        'nlp = get_nlp_model()',
                        new_content
                    )
                    
                    # Replace direct spacy usage
                    new_content = re.sub(
                        r'\bspacy\.([a-zA-Z_][a-zA-Z0-9_]*)',
                        lambda m: f'get_nlp_model().{m.group(1)}' if m.group(1) != 'load' else 'get_nlp_model()',
                        new_content
                    )
                    
                    # Write the fixed file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    rules_fixed += 1
                    print(f"   ✅ Fixed {filename}")
                    
                else:
                    rules_skipped += 1
                    print(f"   ⏭️ Skipped {filename} (no spaCy import)")
                    
            except Exception as e:
                print(f"   ❌ Error fixing {filename}: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Rules fixed: {rules_fixed}")
    print(f"   Rules skipped: {rules_skipped}")
    print(f"   \n🎯 Expected performance improvement:")
    print(f"   Before: 27s+ (each rule loads spaCy)")
    print(f"   After: <1s (shared spaCy utility)")

if __name__ == "__main__":
    fix_spacy_imports()
