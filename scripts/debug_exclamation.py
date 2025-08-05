#!/usr/bin/env python3
"""
Debug the exclamation mark filtering
"""

import re

def debug_exclamation_filtering():
    # Test content similar to what might be causing the issue
    test_content = """> **NOTE**! This is important information.

This document has regular content.

> **WARNING**! Be careful with this operation."""

    print("Original content:")
    print(repr(test_content))
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
    
    # Test each pattern
    for i, pattern in enumerate(note_patterns):
        matches = re.findall(pattern, test_content, flags=re.MULTILINE)
        print(f"Pattern {i+1}: {pattern}")
        print(f"Matches: {matches}")
        print()
    
    # Apply filtering
    filtered_text = test_content
    print("Applying filters...")
    
    for pattern in note_patterns:
        old_text = filtered_text
        filtered_text = re.sub(pattern, lambda m: m.group().replace('!', ''), filtered_text, flags=re.MULTILINE)
        if old_text != filtered_text:
            print(f"Pattern matched and filtered: {pattern}")
    
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
        print(f"Ratio: {ratio} (threshold: 0.1)")
        if ratio > 0.1:
            print("⚠️ Would trigger warning")
        else:
            print("✅ Would NOT trigger warning")

if __name__ == "__main__":
    debug_exclamation_filtering()
