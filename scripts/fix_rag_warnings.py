#!/usr/bin/env python3
"""
Fix RAG warning messages across all rule files.
This script changes logging.warning to logging.debug for RAG availability messages.
"""

import os
import re
from pathlib import Path

def fix_rag_warnings():
    """Update all rule files to use debug logging instead of warning for RAG messages."""
    
    rules_dir = Path("app/rules")
    
    if not rules_dir.exists():
        print("❌ Rules directory not found!")
        return
    
    pattern = re.compile(
        r'logging\.warning\(f"RAG helper not available for \{__name__\}"\)',
        re.MULTILINE
    )
    
    replacement = 'logging.debug(f"RAG helper not available for {__name__} - using basic rules")'
    
    updated_files = []
    
    for rule_file in rules_dir.glob("*.py"):
        if rule_file.name == "__init__.py":
            continue
            
        try:
            # Read the file
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it needs updating
            if 'logging.warning(f"RAG helper not available for {__name__}")' in content:
                # Update the content
                new_content = content.replace(
                    'logging.warning(f"RAG helper not available for {__name__}")',
                    'logging.debug(f"RAG helper not available for {__name__} - using basic rules")'
                )
                
                # Write back the file
                with open(rule_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(rule_file.name)
                print(f"✅ Updated: {rule_file.name}")
        
        except Exception as e:
            print(f"❌ Error updating {rule_file.name}: {e}")
    
    print(f"\n🎉 Successfully updated {len(updated_files)} files!")
    
    if updated_files:
        print("\nUpdated files:")
        for filename in sorted(updated_files):
            print(f"  • {filename}")
    
    print("\n💡 Now restart your app - the warnings should be gone!")

if __name__ == "__main__":
    print("🔧 Fixing RAG warning messages in rule files...")
    print("=" * 50)
    fix_rag_warnings()
