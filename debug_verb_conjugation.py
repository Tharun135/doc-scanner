#!/usr/bin/env python3
"""
Debug the verb conjugation logic.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def debug_verb_conjugation():
    """Debug the verb conjugation logic."""
    
    test_cases = [
        "supporteds",
        "provideds", 
        "createds",
        "updateds",
        "processeds",
        "configureds",
        "executeds"
    ]
    
    print("Debugging verb conjugation:")
    
    for word in test_cases:
        # Extract base word (remove 'eds')
        if word.endswith('eds'):
            base_word = word[:-3]  # Remove 'eds'
            print(f"\nWord: {word}")
            print(f"Base: {base_word}")
            
            # Apply conjugation rules
            base_lower = base_word.lower()
            
            # Check specific mappings first
            verb_corrections = {
                'support': 'supports',
                'provide': 'provides', 
                'create': 'creates',
                'update': 'updates',
                'process': 'processes',
                'configure': 'configures',
                'execute': 'executes'
            }
            
            if base_lower in verb_corrections:
                correct_form = verb_corrections[base_lower]
                print(f"Found in mapping: {correct_form}")
            else:
                # Apply rules
                if base_lower.endswith('e'):
                    correct_form = base_word + 's'
                    print(f"Rule (ends with e): {correct_form}")
                elif base_lower.endswith('y') and len(base_word) > 1 and base_word[-2] not in 'aeiou':
                    correct_form = base_word[:-1] + 'ies'
                    print(f"Rule (ends with consonant+y): {correct_form}")
                elif base_lower.endswith(('s', 'ss', 'sh', 'ch', 'x', 'z', 'o')):
                    correct_form = base_word + 'es'
                    print(f"Rule (sibilant ending): {correct_form}")
                else:
                    correct_form = base_word + 's'
                    print(f"Rule (default): {correct_form}")

if __name__ == "__main__":
    debug_verb_conjugation()
