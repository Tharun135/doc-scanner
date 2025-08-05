#!/usr/bin/env python3
"""
Test the updated patterns
"""

import re
from bs4 import BeautifulSoup
import html

def test_updated_patterns():
    """Test the new comprehensive patterns"""
    
    # Updated patterns from the fix
    note_patterns = [
        # Blockquote patterns with ** (markdown)
        r'(?i)^[ \t]*>[ \t]*\*\*note\*\*[!\s]*',      # > **NOTE**!
        r'(?i)^[ \t]*>[ \t]*\*\*notice\*\*[!\s]*',    # > **NOTICE**!
        r'(?i)^[ \t]*>[ \t]*\*\*warning\*\*[!\s]*',   # > **WARNING**!
        
        # Blockquote patterns without ** (after HTML processing)
        r'(?i)^[ \t]*>[ \t]*note[!\s]*',              # > NOTE!
        r'(?i)^[ \t]*>[ \t]*notice[!\s]*',            # > NOTICE!
        r'(?i)^[ \t]*>[ \t]*warning[!\s]*',           # > WARNING!
        
        # Bold patterns with colons
        r'(?i)^[ \t]*\*\*note\*\*[!\s]*:',            # **NOTE**!:
        r'(?i)^[ \t]*\*\*notice\*\*[!\s]*:',          # **NOTICE**!:
        r'(?i)^[ \t]*\*\*warning\*\*[!\s]*:',         # **WARNING**!:
        
        # Bold patterns without colons
        r'(?i)^[ \t]*\*\*note\*\*[!\s]*',             # **NOTE**!
        r'(?i)^[ \t]*\*\*notice\*\*[!\s]*',           # **NOTICE**!
        r'(?i)^[ \t]*\*\*warning\*\*[!\s]*',          # **WARNING**!
        
        # Simple patterns with colons
        r'(?i)^[ \t]*note[!\s]*:',                    # NOTE!:
        r'(?i)^[ \t]*notice[!\s]*:',                  # NOTICE!:
        r'(?i)^[ \t]*warning[!\s]*:',                 # WARNING!:
        
        # Simple patterns without colons (at start of line)
        r'(?i)^[ \t]*note[!\s]*(?=\s)',               # NOTE! (followed by space)
        r'(?i)^[ \t]*notice[!\s]*(?=\s)',             # NOTICE! (followed by space)
        r'(?i)^[ \t]*warning[!\s]*(?=\s)',            # WARNING! (followed by space)
    ]
    
    test_cases = [
        # Case 1: Standard markdown
        "> **NOTE**! This is important.",
        
        # Case 2: HTML processed
        "> NOTE! This is important information.",
        
        # Case 3: Bold without blockquote
        "**NOTE**! This is a note.",
        
        # Case 4: Simple NOTE
        "NOTE! This is another note.",
        
        # Case 5: With colons
        "NOTE!: Important information follows.",
        
        # Case 6: Multiple NOTEs
        """> **NOTE**! First note.
**WARNING**! Second warning.
NOTICE! Third notice.""",
    ]
    
    for i, content in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"TEST {i}: {content}")
        print('='*50)
        
        # Process like in tone_voice.py
        soup = BeautifulSoup(content, "html.parser")
        text_content = soup.get_text()
        text_content = html.unescape(text_content)
        
        print(f"Processed text: {repr(text_content)}")
        
        filtered_text = text_content
        matched_patterns = []
        
        for j, pattern in enumerate(note_patterns):
            old_text = filtered_text
            matches = re.findall(pattern, filtered_text, flags=re.MULTILINE)
            if matches:
                matched_patterns.append(f"Pattern {j+1}: {matches}")
                filtered_text = re.sub(pattern, lambda m: m.group().replace('!', ''), filtered_text, flags=re.MULTILINE)
        
        original_exclamations = text_content.count('!')
        filtered_exclamations = filtered_text.count('!')
        sentence_count = len(re.findall(r'[.!?]+', text_content))
        
        print(f"Matched patterns: {matched_patterns}")
        print(f"Original exclamations: {original_exclamations}")
        print(f"Filtered exclamations: {filtered_exclamations}")
        print(f"Sentence count: {sentence_count}")
        
        if sentence_count > 0:
            ratio = filtered_exclamations / sentence_count
            print(f"Ratio: {ratio:.3f}")
            if ratio > 0.1:
                print("⚠️ WOULD TRIGGER WARNING")
            else:
                print("✅ Would NOT trigger warning")

if __name__ == "__main__":
    test_updated_patterns()
