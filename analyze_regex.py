#!/usr/bin/env python3
"""
Detailed analysis of why the sentence matches the long sentence pattern
"""

import re

def analyze_regex_pattern():
    sentence = "Autostart feature is beneficial in cases where an application or an IED is restarted."
    
    # The exact pattern from clarity_fixed.py
    pattern = r'[A-Z][^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*(?:,|\s+(?:and|or|but|because|since|although|while|when|where|if))[^.!?]*[.!?]'
    
    print(f"Sentence: {sentence}")
    print(f"Pattern: {pattern}")
    print()
    
    # Break down the pattern
    print("Pattern breakdown:")
    print("1. [A-Z] - Starts with capital letter: ✓ 'A' in 'Autostart'")
    print("2. [^.!?]* - Any characters except sentence endings")
    print("3. (?:,|\\s+(?:and|or|but|because|since|although|while|when|where|if)) - First conjunction/comma")
    print("4. [^.!?]* - More characters")
    print("5. (?:,|\\s+(?:and|or|but|because|since|although|while|when|where|if)) - Second conjunction/comma")
    print("6. [^.!?]* - More characters")
    print("7. [.!?] - Ends with sentence terminator")
    print()
    
    # Find all conjunctions in the sentence
    conjunctions = ['and', 'or', 'but', 'because', 'since', 'although', 'while', 'when', 'where', 'if']
    found_positions = []
    
    for conj in conjunctions:
        pattern_conj = r'\s+' + re.escape(conj) + r'\b'
        matches = list(re.finditer(pattern_conj, sentence, re.IGNORECASE))
        for match in matches:
            found_positions.append((conj, match.start(), match.end(), match.group()))
    
    found_positions.sort(key=lambda x: x[1])  # Sort by position
    
    print("Conjunctions found:")
    for conj, start, end, matched_text in found_positions:
        print(f"  '{conj}' at position {start}-{end}: '{matched_text}'")
    
    print()
    
    # Show why it matches
    if len(found_positions) >= 2:
        print(f"✓ MATCHES: Found {len(found_positions)} conjunctions, pattern requires 2+")
        print("  The pattern detects sentences with multiple conjunctions as potentially complex")
        print("  Even though word count is only 14, the structure suggests multiple clauses")
    else:
        print(f"✗ DOESN'T MATCH: Only found {len(found_positions)} conjunction(s), pattern requires 2+")

if __name__ == "__main__":
    analyze_regex_pattern()
