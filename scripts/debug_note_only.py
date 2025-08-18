#!/usr/bin/env python3
"""
Debug with the actual NOTE-only content
"""

import re

def debug_note_only():
    # Read the actual note template file
    with open('test_note_only.md', 'r') as f:
        test_content = f.read()
    
    print("Content being tested:")
    print(repr(test_content))
    print()
    print("Visual content:")
    print(test_content)
    print()
    
    # The patterns from tone_voice.py
    note_patterns = [
        r'(?i)^[ \t]*>[ \t]*\*\*note\*\*[!\s]*',  # > **NOTE**!
        r'(?i)^[ \t]*>[ \t]*note[!\s]*:',          # > NOTE!:
        r'(?i)^[ \t]*\*\*note\*\*[!\s]*:',        # **NOTE**!:
        r'(?i)^[ \t]*note[!\s]*:',                 # NOTE!:
        r'(?i)^[ \t]*>[ \t]*\*\*notice\*\*[!\s]*', # > **NOTICE**!
        r'(?i)^[ \t]*>[ \t]*notice[!\s]*:',        # > NOTICE!:
        r'(?i)^[ \t]*\*\*notice\*\*[!\s]*:',      # **NOTICE**!:
        r'(?i)^[ \t]*notice[!\s]*:',               # NOTICE!:
        r'(?i)^[ \t]*>[ \t]*\*\*warning\*\*[!\s]*', # > **WARNING**!
        r'(?i)^[ \t]*>[ \t]*warning[!\s]*:',       # > WARNING!:
        r'(?i)^[ \t]*\*\*warning\*\*[!\s]*:',     # **WARNING**!:
        r'(?i)^[ \t]*warning[!\s]*:',              # WARNING!:
    ]
    
    # Apply filtering like in tone_voice.py
    filtered_text = test_content
    
    for pattern in note_patterns:
        old_text = filtered_text
        filtered_text = re.sub(pattern, lambda m: m.group().replace('!', ''), filtered_text, flags=re.MULTILINE)
        if old_text != filtered_text:
            print(f"✅ Pattern matched and filtered: {pattern}")
    
    print()
    print("Filtered content:")
    print(repr(filtered_text))
    print()
    
    original_exclamations = test_content.count('!')
    filtered_exclamations = filtered_text.count('!')
    
    print(f"Original exclamation count: {original_exclamations}")
    print(f"Filtered exclamation count: {filtered_exclamations}")
    
    sentence_count = len(re.findall(r'[.!?]+', test_content))
    print(f"Sentence count: {sentence_count}")
    
    if sentence_count > 0:
        ratio = filtered_exclamations / sentence_count
        print(f"Ratio: {ratio:.3f} (threshold: 0.1)")
        if ratio > 0.1:
            print("⚠️ Would trigger warning")
        else:
            print("✅ Would NOT trigger warning")

if __name__ == "__main__":
    debug_note_only()
