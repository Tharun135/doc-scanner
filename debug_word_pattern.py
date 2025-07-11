#!/usr/bin/env python3
"""
Debug the word matching for documents
"""

import re

def test_word_pattern():
    """Test word pattern matching"""
    
    # Test text
    text = "Backup your important documents regularly"
    
    # Test different word patterns
    patterns = [
        r'documents?',
        r'documents',
        r'document',
        r'(files?|data|documents?)'
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern}")
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
        print(f"Matches: {len(matches)}")
        for match in matches:
            print(f"  Match: '{match.group()}' at position {match.start()}-{match.end()}")
        print()
    
    # Test the full pattern with word boundaries
    full_pattern = r'\bbackup\s+(your|the|all)\s+(files?|data|documents?)\b'
    print(f"Full pattern: {full_pattern}")
    matches = list(re.finditer(full_pattern, text, flags=re.IGNORECASE))
    print(f"Matches: {len(matches)}")
    for match in matches:
        print(f"  Match: '{match.group()}' at position {match.start()}-{match.end()}")

if __name__ == "__main__":
    test_word_pattern()
