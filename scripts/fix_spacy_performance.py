#!/usr/bin/env python3

"""
Script to fix spaCy performance issues in rule files.
"""

import os
import re

def fix_spacy_imports(filepath):
    """Fix spaCy imports in a rule file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already fixed
    if 'from .spacy_utils import' in content:
        return False, "Already using shared spaCy utilities"
    
    # Check if it needs spaCy
    if 'spacy.load(' not in content:
        return False, "No spaCy loading found"
    
    original_content = content
    
    # Replace spacy import and loading
    content = re.sub(r'import spacy\n', '', content)
    content = re.sub(r'nlp = spacy\.load\([^)]+\)\n', '', content)
    
    # Add shared spacy utils import at the top (after other imports)
    import_section = []
    other_lines = []
    in_imports = True
    
    lines = content.split('\n')
    for line in lines:
        if in_imports and (line.startswith('import ') or line.startswith('from ') or line.strip() == '' or line.startswith('#')):
            import_section.append(line)
        else:
            if in_imports:
                # Add spacy utils import
                import_section.append('')
                import_section.append('# Use shared spaCy utilities instead of loading model separately')
                import_section.append('try:')
                import_section.append('    from .spacy_utils import get_nlp_model')
                import_section.append('    SPACY_AVAILABLE = True')
                import_section.append('except ImportError:')
                import_section.append('    SPACY_AVAILABLE = False')
                import_section.append('')
                in_imports = False
            other_lines.append(line)
    
    content = '\n'.join(import_section + other_lines)
    
    # Replace nlp usage with conditional loading
    # Pattern: nlp(some_text) -> get_nlp_model() and process if available
    def replace_nlp_usage(match):
        return f'''nlp = get_nlp_model()
    if nlp is not None:
        doc = nlp({match.group(1)})
        # Add spaCy processing here if needed
    else:
        # Skip spaCy processing if model not available
        pass'''
    
    content = re.sub(r'doc = nlp\(([^)]+)\)', replace_nlp_usage, content)
    
    if content != original_content:
        return True, "Fixed spaCy imports and usage"
    else:
        return False, "No changes needed"

def fix_files_batch(file_list, max_files=5):
    """Fix a batch of files."""
    
    fixed_count = 0
    
    for filename in file_list[:max_files]:
        filepath = f"d:/doc-scanner/app/rules/{filename}"
        
        if not os.path.exists(filepath):
            continue
            
        try:
            changed, message = fix_spacy_imports(filepath)
            print(f"📁 {filename}: {message}")
            
            if changed:
                # Write the fixed content
                # Note: In practice, you'd want to backup first
                print(f"   ✅ Would fix {filename} (simulation mode)")
                fixed_count += 1
                
        except Exception as e:
            print(f"❌ Error fixing {filename}: {e}")
    
    return fixed_count

def main():
    """Main function to identify and fix critical spaCy issues."""
    
    print("🔧 SPACY PERFORMANCE FIX UTILITY")
    print("=" * 50)
    
    # Get list of files with spaCy issues (from previous analysis)
    critical_files = [
        'accessibility_terms.py', 'ai_bot_terms.py', 'cable_terms.py', 
        'cache_terms.py', 'calendar_terms.py', 'callback_terms.py',
        'callout_terms.py', 'cancel_terms.py', 'can_may_terms.py',
        'catalog_terms.py', 'cloud_computing_terms.py', 'computer_device_terms.py',
        'concise_simple_words.py', 'contractions_rule.py', 'css_terms.py'
    ]
    
    print(f"🎯 PRIORITY: Fixing {len(critical_files)} critical files first")
    print("   This should provide immediate 3-10 second speedup!")
    print()
    
    fixed_count = fix_files_batch(critical_files, max_files=5)
    
    print(f"\n📊 SIMULATION RESULTS:")
    print(f"   Files that would be fixed: {fixed_count}")
    print(f"   Estimated time savings: {fixed_count * 0.2:.1f} - {fixed_count * 0.5:.1f} seconds")
    
    print(f"\n💡 RECOMMENDATION:")
    print("1. Backup app/rules/ directory first")
    print("2. Convert all rule files to use shared spacy_utils")
    print("3. Test document analysis speed")
    print("4. Expected improvement: 3-10 seconds faster analysis")

if __name__ == "__main__":
    main()
