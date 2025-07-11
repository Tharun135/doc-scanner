#!/usr/bin/env python3
"""
Debug the imperative pattern for backup
"""

import re

def test_imperative_pattern():
    """Test the imperative pattern matching"""
    
    # Test text
    text = "Backup your important documents regularly"
    
    # Test patterns
    patterns = [
        r'(?:^|\.\s*)backup\s+(your|the|all)\s+(files?|data|documents?)\b',
        r'^backup\s+(your|the|all)\s+(files?|data|documents?)\b',
        r'\bbackup\s+(your|the|all)\s+(files?|data|documents?)\b'
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern}")
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
        print(f"Matches: {len(matches)}")
        for match in matches:
            print(f"  Match: '{match.group()}' at position {match.start()}-{match.end()}")
        print()

if __name__ == "__main__":
    test_imperative_pattern()
