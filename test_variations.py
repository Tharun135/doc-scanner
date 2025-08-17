#!/usr/bin/env python3
"""
Test possible variations of the text that might trigger the space before punctuation issue
"""

from app.rules.formatting_fixed import check
import re

def test_variations():
    print("=== TESTING POSSIBLE VARIATIONS ===\n")
    
    # Possible variations that might cause the issue
    variations = [
        # Original text
        """Prerequisite
The WinCC Unified Runtime app must be running.
A proj""",
        
        # With space before period
        """Prerequisite
The WinCC Unified Runtime app must be running .
A proj""",
        
        # With trailing spaces
        """Prerequisite 
The WinCC Unified Runtime app must be running.
A proj """,
        
        # With space before colon (common in headings)
        """Prerequisite :
The WinCC Unified Runtime app must be running.
A proj""",
        
        # With other punctuation
        """Prerequisite,
The WinCC Unified Runtime app must be running .
A proj !""",
        
        # Complete sentence that might have the issue
        """Prerequisite:
The WinCC Unified Runtime app must be running.
A project must be configured .""",
        
        # Check if it's about the incomplete "A proj"
        """Prerequisite
The WinCC Unified Runtime app must be running.
A project ."""
    ]
    
    for i, text in enumerate(variations, 1):
        print(f"VARIATION {i}:")
        print(f"Text: '''{repr(text)}'''")
        
        # Run formatting check
        results = check(text)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        if space_issues:
            print("❌ FLAGGED for space before punctuation:")
            for issue in space_issues:
                print(f"   '{issue['text']}' at position {issue['start']}-{issue['end']}")
                # Show the actual characters
                flagged_chars = issue['text']
                char_info = []
                for char in flagged_chars:
                    if char == ' ':
                        char_info.append('SPACE')
                    elif char in '.!?,:;':
                        char_info.append(f"'{char}'")
                    else:
                        char_info.append(f"'{char}'")
                print(f"   Characters: {' + '.join(char_info)}")
        else:
            print("✅ No space before punctuation issues")
        
        print("-" * 50)

def check_invisible_characters():
    print("\n=== CHECKING FOR INVISIBLE CHARACTERS ===\n")
    
    # Your original text - let's check for invisible characters
    original = """Prerequisite
The WinCC Unified Runtime app must be running.
A proj"""
    
    print("Character-by-character analysis:")
    for i, char in enumerate(original):
        if char == ' ':
            print(f"{i:3d}: SPACE")
        elif char == '\n':
            print(f"{i:3d}: NEWLINE")
        elif char == '\t':
            print(f"{i:3d}: TAB")
        elif char in '.!?,:;':
            print(f"{i:3d}: PUNCTUATION '{char}'")
        elif ord(char) > 127:
            print(f"{i:3d}: UNICODE '{char}' (code: {ord(char)})")
        else:
            print(f"{i:3d}: '{char}'")

if __name__ == "__main__":
    test_variations()
    check_invisible_characters()
