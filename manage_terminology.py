#!/usr/bin/env python3
"""
Utility script to manage custom terminology for spell checking.
Allows adding, removing, and viewing terms in the custom whitelist.
"""

import sys
import os
import argparse

# Add the app directory to the path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from custom_terminology import get_terminology_manager

def main():
    parser = argparse.ArgumentParser(
        description="Manage custom terminology for spell checking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    # List all custom terms
  %(prog)s add runtime             # Add 'runtime' to whitelist
  %(prog)s add runtime wincc hmi   # Add multiple terms
  %(prog)s remove runtime          # Remove 'runtime' from whitelist
  %(prog)s check runtime           # Check if 'runtime' is whitelisted
  %(prog)s count                   # Show number of terms
        """
    )
    
    parser.add_argument(
        'action',
        choices=['list', 'add', 'remove', 'check', 'count', 'clear'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'terms',
        nargs='*',
        help='Terms to add, remove, or check'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        default=True,
        help='Save changes to file (default: True)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to custom terminology configuration file'
    )
    
    args = parser.parse_args()
    
    # Initialize terminology manager
    manager = get_terminology_manager() if not args.config else None
    if args.config:
        from custom_terminology import CustomTerminologyManager
        manager = CustomTerminologyManager(args.config)
    
    # Execute the requested action
    if args.action == 'list':
        terms = manager.get_all_terms()
        if terms:
            print(f"Custom terminology ({len(terms)} terms):")
            for i, term in enumerate(terms, 1):
                print(f"  {i:3d}. {term}")
        else:
            print("No custom terms defined.")
    
    elif args.action == 'count':
        count = manager.get_terms_count()
        print(f"Total custom terms: {count}")
    
    elif args.action == 'add':
        if not args.terms:
            print("Error: No terms specified to add.", file=sys.stderr)
            return 1
        
        added_count = 0
        for term in args.terms:
            if manager.add_term(term):
                print(f"Added: {term}")
                added_count += 1
            else:
                print(f"Already exists: {term}")
        
        if added_count > 0 and args.save:
            if manager.save_custom_terms():
                print(f"Saved {added_count} new term(s) to configuration.")
            else:
                print("Error: Failed to save changes.", file=sys.stderr)
                return 1
    
    elif args.action == 'remove':
        if not args.terms:
            print("Error: No terms specified to remove.", file=sys.stderr)
            return 1
        
        removed_count = 0
        for term in args.terms:
            if manager.remove_term(term):
                print(f"Removed: {term}")
                removed_count += 1
            else:
                print(f"Not found: {term}")
        
        if removed_count > 0 and args.save:
            if manager.save_custom_terms():
                print(f"Saved changes after removing {removed_count} term(s).")
            else:
                print("Error: Failed to save changes.", file=sys.stderr)
                return 1
    
    elif args.action == 'check':
        if not args.terms:
            print("Error: No terms specified to check.", file=sys.stderr)
            return 1
        
        for term in args.terms:
            is_whitelisted = manager.is_whitelisted(term)
            status = "YES" if is_whitelisted else "NO"
            print(f"{term}: {status}")
    
    elif args.action == 'clear':
        confirm = input("Are you sure you want to clear all custom terms? (y/N): ")
        if confirm.lower() == 'y':
            manager.clear_all_terms()
            if args.save:
                if manager.save_custom_terms():
                    print("Cleared all custom terms.")
                else:
                    print("Error: Failed to save changes.", file=sys.stderr)
                    return 1
        else:
            print("Operation cancelled.")
    
    return 0

if __name__ == "__main__":
    exit(main())
