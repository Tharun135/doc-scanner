#!/usr/bin/env python3
"""
Quick test for the specific passive voice issue.
"""

import re

def test_pattern_matching():
    """Test the specific patterns that should match the problematic sentence."""
    
    test_sentence = "It is utilized when a provided configuration file needs to be converted to the format used by the"
    
    print(f"Testing sentence: {test_sentence}")
    print("-" * 50)
    
    # Test individual patterns
    patterns = [
        (r'\bit\s+is\s+utilized\b', "it is utilized"),
        (r'\bit\s+is\s+used\b', "it is used"),
        (r'\bneeds\s+to\s+be\s+\w+ed\b', "needs to be [verb]ed"),
        (r'\bneed\s+to\s+be\s+\w+ed\b', "need to be [verb]ed"),
    ]
    
    for pattern, description in patterns:
        match = re.search(pattern, test_sentence, re.IGNORECASE)
        print(f"Pattern '{description}': {'MATCH' if match else 'NO MATCH'}")
        if match:
            print(f"  Matched text: '{match.group()}'")
    
    print("\n" + "=" * 50)
    print("TESTING REWRITE PATTERNS")
    print("=" * 50)
    
    # Test rewrite patterns
    sentence_lower = test_sentence.lower()
    
    # Pattern 1: "It is utilized when..." -> "Use it when..."
    if re.search(r'it\s+is\s+utilized\s+when', sentence_lower):
        rewrite = re.sub(r'it\s+is\s+utilized\s+when\s+(.+)', 
                       r'Use it when \1', 
                       test_sentence, flags=re.IGNORECASE)
        print(f"Pattern 1 rewrite: {rewrite}")
    
    # Pattern 2: "X needs to be converted" -> "You need to convert X"
    if re.search(r'(.+?)\s+needs?\s+to\s+be\s+(\w+ed)', sentence_lower):
        match = re.search(r'(.+?)\s+needs?\s+to\s+be\s+(\w+ed)(.+)', sentence_lower)
        if match:
            object_part = match.group(1).strip()
            verb = match.group(2)
            remainder = match.group(3).strip()
            
            # Convert verb
            verb_conversions = {
                "converted": "convert", "created": "create", "generated": "generate"
            }
            verb_active = verb_conversions.get(verb.lower(), verb)
            
            if remainder:
                rewrite = f"You need to {verb_active} {object_part}{remainder}."
            else:
                rewrite = f"You need to {verb_active} {object_part}."
            
            print(f"Pattern 2 rewrite: {rewrite}")

if __name__ == "__main__":
    test_pattern_matching()
