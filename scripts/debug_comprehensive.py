#!/usr/bin/env python3
"""
Advanced debug to understand why the fix isn't working
"""

import re
import sys
import os
from bs4 import BeautifulSoup
import html

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.rules.title_utils import is_title_or_heading
    import spacy
    nlp_loaded = spacy.load("en_core_web_sm")
    TITLE_UTILS_AVAILABLE = True
except Exception:
    TITLE_UTILS_AVAILABLE = False
    nlp_loaded = None

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.rules.title_utils import is_title_or_heading
    import spacy
    nlp_loaded = spacy.load("en_core_web_sm")
    TITLE_UTILS_AVAILABLE = True
except Exception:
    TITLE_UTILS_AVAILABLE = False
    nlp_loaded = None

def debug_tone_voice_detailed():
    """Recreate the exact logic from tone_voice.py to debug"""
    
    # Test with various NOTE formats that might be causing issues
    test_cases = [
        # Case 1: Standard NOTE format
        "> **NOTE**! This is important information.",
        
        # Case 2: NOTE with multiple exclamations
        "> **NOTE**! This is important! Really important! Very important!",
        
        # Case 3: Mixed content
        """> **NOTE**! This is important information.

This document has regular content with exclamation marks! Some are excessive! Others are normal!""",
        
        # Case 4: Different NOTE formats
        """**NOTE**! This is a note.
NOTE! This is another note.
> NOTE! This is a blockquote note.""",
        
        # Case 5: HTML content (from web upload)
        """<p>&gt; <strong>NOTE</strong>! This is important information.</p>
<p>Regular content follows! With exclamation marks!</p>"""
    ]
    
    for i, content in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST CASE {i}")
        print(f"{'='*60}")
        print("Raw content:")
        print(repr(content))
        print("\nVisual content:")
        print(content)
        print()
        
        # Simulate the tone_voice.py processing
        simulate_tone_voice_processing(content)

def simulate_tone_voice_processing(content):
    """Simulate exactly what happens in tone_voice.py"""
    
    print("🔄 Processing like tone_voice.py...")
    
    # Step 1: Strip HTML tags from content (like in tone_voice.py)
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    print(f"After HTML processing: {repr(text_content)}")
    
    # Step 2: Apply the NOTE pattern filtering
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
    
    print("\n📋 Testing each pattern:")
    filtered_text = text_content
    patterns_matched = []
    
    for j, pattern in enumerate(note_patterns):
        old_text = filtered_text
        matches = re.findall(pattern, filtered_text, flags=re.MULTILINE)
        
        if matches:
            patterns_matched.append((j+1, pattern, matches))
            print(f"   ✅ Pattern {j+1} matched: {matches}")
            # Apply the filter
            filtered_text = re.sub(pattern, lambda m: m.group().replace('!', ''), filtered_text, flags=re.MULTILINE)
        else:
            print(f"   ❌ Pattern {j+1} no match")
    
    print(f"\n📊 Results:")
    print(f"   Original text: {repr(text_content)}")
    print(f"   Filtered text: {repr(filtered_text)}")
    
    original_exclamations = text_content.count('!')
    filtered_exclamations = filtered_text.count('!')
    
    # Count sentences excluding headings
    if TITLE_UTILS_AVAILABLE and nlp_loaded:
        try:
            doc = nlp_loaded(text_content)
            # Count only non-heading sentences
            sentence_count = sum(1 for sent in doc.sents 
                               if not is_title_or_heading(sent.text.strip(), content))
        except Exception:
            # Fallback if spaCy processing fails
            sentence_count = len(re.findall(r'[.!?]+', text_content))
    else:
        # Fallback: count all sentence-ending punctuation
        sentence_count = len(re.findall(r'[.!?]+', text_content))
    
    print(f"   Original exclamation count: {original_exclamations}")
    print(f"   Filtered exclamation count: {filtered_exclamations}")
    print(f"   Sentence count (excluding headings): {sentence_count}")
    
    if sentence_count > 0:
        ratio = filtered_exclamations / sentence_count
        print(f"   Ratio: {ratio:.3f} (threshold: 0.1)")
        if ratio > 0.1:
            print(f"   ⚠️ WOULD TRIGGER WARNING: Excessive exclamation marks ({filtered_exclamations})")
        else:
            print(f"   ✅ Would NOT trigger warning")
    
    return patterns_matched, filtered_exclamations, sentence_count

if __name__ == "__main__":
    debug_tone_voice_detailed()
