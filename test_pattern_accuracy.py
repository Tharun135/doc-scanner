#!/usr/bin/env python3
"""
Test improved patterns for list-aware punctuation spacing
"""

import re

def test_improved_patterns():
    print("=== TESTING IMPROVED PATTERNS ===\n")
    
    # Test cases
    test_cases = [
        # Should be ALLOWED (list formatting)
        ("Prerequisite:\n- The app must be running .", "List with dash", True),
        ("Steps:\n• First item .", "List with bullet", True),
        ("Notes:\n* Important point .", "List with asterisk", True),
        ("Requirements:\n1. First item .", "Numbered list", True),
        ("Items:\n  - Indented item .", "Indented list", True),
        
        # Should be FLAGGED (regular text)
        ("This is wrong . Regular text.", "Regular sentence", False),
        ("Hello , world", "Regular comma spacing", False),
        ("What ? This is wrong.", "Regular question", False),
        ("End of sentence .", "Regular period", False),
    ]
    
    # Different pattern approaches
    patterns = [
        {
            "name": "Original (flags everything)",
            "pattern": r'\s+[.!?,:;]',
            "description": "Current pattern - flags all spaces before punctuation"
        },
        {
            "name": "Exclude lines with bullets",
            "pattern": r'(?<![-*•·] )\s+[.!?,:;]',
            "description": "Don't flag if preceded by bullet and space"
        },
        {
            "name": "Exclude list lines completely",
            "pattern": r'(?<!^[\s]*[-*•·] .*)\s+[.!?,:;]',
            "description": "Don't flag if line starts with bullet (fixed width)"
        },
        {
            "name": "Smart exclusion",
            "pattern": r'(?<![-*•·] .{1,50})\s+[.!?,:;]',
            "description": "Don't flag within 50 chars after bullet"
        }
    ]
    
    for pattern_info in patterns:
        print(f"PATTERN: {pattern_info['name']}")
        print(f"Regex: {pattern_info['pattern']}")
        print(f"Description: {pattern_info['description']}")
        print("-" * 60)
        
        correct_count = 0
        total_count = len(test_cases)
        
        for text, description, should_allow in test_cases:
            match = re.search(pattern_info['pattern'], text, re.MULTILINE)
            is_flagged = match is not None
            
            # Check if behavior is correct
            correct_behavior = (should_allow and not is_flagged) or (not should_allow and is_flagged)
            
            status = "✅" if correct_behavior else "❌"
            flag_status = "FLAGGED" if is_flagged else "ALLOWED"
            expected = "ALLOW" if should_allow else "FLAG"
            
            print(f"{status} {description}: {flag_status} (expected: {expected})")
            
            if match and is_flagged:
                print(f"    Matched: '{match.group()}' at position {match.start()}")
            
            if correct_behavior:
                correct_count += 1
        
        accuracy = (correct_count / total_count) * 100
        print(f"\nAccuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
        print("=" * 60)
        print()

if __name__ == "__main__":
    test_improved_patterns()
