#!/usr/bin/env python3
"""
Remove RAG debug messages from all rule files.
This script completely removes the debug logging lines.
"""

import os
import re
from pathlib import Path

def remove_rag_debug_messages():
    """Remove debug logging lines from all rule files."""
    
    rules_dir = Path("app/rules")
    
    if not rules_dir.exists():
        print("❌ Rules directory not found!")
        return
    
    updated_files = []
    
    for rule_file in rules_dir.glob("*.py"):
        if rule_file.name == "__init__.py":
            continue
            
        try:
            # Read the file
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it needs updating
            debug_line = 'logging.debug(f"RAG helper not available for {__name__} - using basic rules")'
            if debug_line in content:
                # Remove the debug line (and the import logging if it's only used for this)
                lines = content.split('\n')
                new_lines = []
                skip_import = False
                
                for i, line in enumerate(lines):
                    if debug_line in line:
                        # Skip this line
                        continue
                    elif line.strip() == 'import logging' and i < len(lines) - 1:
                        # Check if the next few lines contain our debug statement
                        next_lines = '\n'.join(lines[i:i+5])
                        if debug_line in next_lines:
                            skip_import = True
                            continue
                    
                    new_lines.append(line)
                
                new_content = '\n'.join(new_lines)
                
                # Write back the file
                with open(rule_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated_files.append(rule_file.name)
                print(f"✅ Cleaned: {rule_file.name}")
        
        except Exception as e:
            print(f"❌ Error updating {rule_file.name}: {e}")
    
    print(f"\n🎉 Successfully cleaned {len(updated_files)} files!")
    
    if updated_files:
        print("\nCleaned files:")
        for filename in sorted(updated_files):
            print(f"  • {filename}")
    
    print("\n💡 Debug messages completely removed!")

if __name__ == "__main__":
    print("🧹 Removing RAG debug messages from rule files...")
    print("=" * 50)
    remove_rag_debug_messages()
