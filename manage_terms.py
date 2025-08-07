#!/usr/bin/env python3
"""
Simple terminology management script.
"""

import sys
import os

# Add app directory to path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
sys.path.insert(0, app_dir)

from simple_terminology import DEFAULT_TERMS, is_custom_whitelisted, add_custom_term

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_terms.py list                 # List all terms")
        print("  python manage_terms.py check <term>         # Check if term is whitelisted")
        print("  python manage_terms.py add <term>           # Add term to whitelist")
        print("  python manage_terms.py count               # Show count of terms")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        print(f"Custom terminology ({len(DEFAULT_TERMS)} terms):")
        for i, term in enumerate(sorted(DEFAULT_TERMS), 1):
            print(f"  {i:3d}. {term}")
    
    elif command == "count":
        print(f"Total custom terms: {len(DEFAULT_TERMS)}")
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Error: Please specify a term to check")
            return
        term = sys.argv[2]
        is_whitelisted = is_custom_whitelisted(term)
        status = "YES" if is_whitelisted else "NO"
        print(f"{term}: {status}")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: Please specify a term to add")
            return
        term = sys.argv[2]
        if add_custom_term(term):
            print(f"Added: {term}")
            # Show updated list
            print(f"Note: To persist this change, edit simple_terminology.py")
        else:
            print(f"Already exists: {term}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
