#!/usr/bin/env python3
"""
Update all rules to use RAG with smart fallback.
This script will modify all rule files to use the RAG helper system.
"""

import os
import sys
import re
from pathlib import Path

def add_rag_imports_to_rule(file_path):
    """Add RAG imports to a rule file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if RAG imports already exist
    if 'rag_rule_helper' in content:
        print(f"✅ {file_path.name} already has RAG imports")
        return False
    
    # Find the import section and add RAG imports
    import_pattern = r'(import spacy\nfrom bs4 import BeautifulSoup\nimport html)'
    rag_imports = '''# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.warning(f"RAG helper not available for {__name__}")'''
    
    # Add imports after existing imports
    if re.search(import_pattern, content):
        new_content = re.sub(
            import_pattern,
            r'\1\n\n' + rag_imports,
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added RAG imports to {file_path.name}")
        return True
    else:
        print(f"⚠️  Could not find import pattern in {file_path.name}")
        return False

def modify_check_function(file_path, rule_name):
    """Modify the check function to use RAG with fallback."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already modified
    if 'check_with_rag' in content:
        print(f"✅ {file_path.name} already has RAG integration")
        return False
    
    # Find the check function
    check_pattern = r'def check\(content\):'
    
    if re.search(check_pattern, content):
        # Create RAG-enhanced check function
        rag_check_function = f'''def check(content):
    """
    Check for {rule_name} issues using RAG with smart fallback.
    Primary: RAG-enhanced suggestions
    Fallback: Rule-based detection
    """
    
    # Use RAG-enhanced checking if available
    if RAG_HELPER_AVAILABLE:
        rule_patterns = {{
            'detect_function': detect_{rule_name}_issues
        }}
        
        fallback_suggestions = [
            "Writing issue detected. Please review for {rule_name} guidelines."
        ]
        
        return check_with_rag(
            content=content,
            rule_patterns=rule_patterns,
            rule_name="{rule_name}",
            fallback_suggestions=fallback_suggestions
        )
    
    # Legacy fallback when RAG helper is not available
    return check_legacy_{rule_name}(content)

def check_legacy_{rule_name}(content):
    """Legacy {rule_name} detection for fallback when RAG is not available."""'''
        
        # Replace the check function
        new_content = re.sub(
            r'def check\(content\):\s*\n',
            rag_check_function + '\n',
            content
        )
        
        # Rename the original function body to legacy
        # This is a bit complex, so we'll do a simple replacement
        new_content = new_content.replace(
            'suggestions = []',
            'suggestions = []  # Legacy implementation',
            1
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Modified check function in {file_path.name}")
        return True
    else:
        print(f"⚠️  Could not find check function in {file_path.name}")
        return False

def create_detection_function(file_path, rule_name):
    """Create a detection function that can be used by the RAG helper."""
    detection_function = f'''
def detect_{rule_name}_issues(content: str, text_content: str):
    """
    Detect {rule_name} issues in text.
    Returns list of detected issues with context.
    """
    import re
    import spacy
    
    issues = []
    
    # Load spaCy if available
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text_content)
    except:
        doc = None
    
    # Add your specific detection logic here
    # This is a template - customize for each rule type
    
    # Example pattern-based detection
    # Replace with actual patterns for your rule
    example_patterns = [
        r'\\bexample\\b',  # Replace with actual patterns
    ]
    
    for pattern in example_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append({{
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "message": f"{rule_name} issue detected: {{match.group()}}",
                "context": text_content[:200]  # First 200 chars as context
            }})
    
    return issues
'''
    
    # Add the detection function to the file
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(detection_function)
    
    print(f"✅ Added detection function to {file_path.name}")

def update_rules_directory():
    """Update all rules in the rules directory."""
    rules_dir = Path(__file__).parent / 'app' / 'rules'
    
    if not rules_dir.exists():
        print(f"❌ Rules directory not found: {rules_dir}")
        return
    
    # Skip these files
    skip_files = {
        '__init__.py', 
        'rag_rule_helper.py', 
        'passive_voice.py',  # Already updated
        'can_may_terms.py',  # Already updated  
        'long_sentences.py'  # Already updated
    }
    
    rule_files = [f for f in rules_dir.glob('*.py') if f.name not in skip_files]
    
    print(f"Found {len(rule_files)} rule files to update")
    print(f"Skipping: {', '.join(skip_files)}")
    
    for rule_file in rule_files:
        print(f"\n📝 Processing {rule_file.name}...")
        
        # Extract rule name from filename
        rule_name = rule_file.stem
        
        # Step 1: Add RAG imports
        add_rag_imports_to_rule(rule_file)
        
        # Step 2: Add generic detection function (can be customized later)
        # create_detection_function(rule_file, rule_name)
        
        # Step 3: Modify check function (skipping for now to avoid breaking)
        # modify_check_function(rule_file, rule_name)
    
    print(f"\n✅ Completed updating rule files")
    print("⚠️  Note: Only imports were added. Manual customization needed for each rule.")

if __name__ == "__main__":
    print("🚀 Starting RAG integration for all rules...")
    update_rules_directory()
    print("\n🎉 RAG integration complete!")
    print("\nNext steps:")
    print("1. Customize detection functions for each rule")
    print("2. Test RAG integration with sample content")
    print("3. Update check functions to use RAG helper")
