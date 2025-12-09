#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup

# Test cases for sentence highlighting issues
test_cases = [
    "The syntax for the URL is as follows: https://<IP_IED>/webrh/<path_to_mediafile>",
    "Use angle brackets like <example> in your documentation.",
    "The path is /usr/local/bin/<filename>.",
    "Configure the setting: <property>value</property>",
    "Normal sentence without special characters."
]

def test_sentence_highlighting():
    print("Testing sentence highlighting for special characters:\n")
    
    for i, sentence in enumerate(test_cases):
        print(f"Test {i+1}: {sentence}")
        
        # Check what rules would trigger (if any)
        from app.rules.concise_simple_words import check
        suggestions = check(sentence)
        
        if suggestions:
            print(f"  Rules triggered: {len(suggestions)}")
            for suggestion in suggestions[:2]:  # Show first 2
                print(f"    - {suggestion}")
        else:
            print("  No rules triggered")
            
        # Analyze potential highlighting issues
        has_angle_brackets = '<' in sentence and '>' in sentence
        has_special_chars = any(char in sentence for char in ['/', ':', '?', '&', '='])
        
        if has_angle_brackets:
            print("  ⚠️  Contains angle brackets - may cause highlighting issues")
        if has_special_chars:
            print("  ⚠️  Contains special URL/path characters")
            
        print()

if __name__ == "__main__":
    test_sentence_highlighting()
