#!/usr/bin/env python3
"""
Debug specific rule execution to understand why title exclusion isn't working
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Test content
test_html = """<h2>Basic Configuration</h2>
<p>This rule checks for several things in your document. You should avoid passive voice construction when possible. The implementation must be done carefully.</p>"""

print("🔍 Testing specific rule functions...")

# Test vague_terms rule
print("\n📝 Testing vague_terms rule:")
try:
    from app.rules.vague_terms import check as vague_check
    from app.rules.vague_terms import TITLE_UTILS_AVAILABLE as vague_title_available
    
    print(f"  - TITLE_UTILS_AVAILABLE: {vague_title_available}")
    vague_results = vague_check(test_html)
    print(f"  - Results: {len(vague_results)} issues")
    for result in vague_results:
        print(f"    • {result}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test passive_voice rule
print("\n📝 Testing passive_voice rule:")
try:
    from app.rules.passive_voice import check as passive_check
    from app.rules.passive_voice import TITLE_UTILS_AVAILABLE as passive_title_available
    
    print(f"  - TITLE_UTILS_AVAILABLE: {passive_title_available}")
    passive_results = passive_check(test_html)
    print(f"  - Results: {len(passive_results)} issues")
    for result in passive_results:
        print(f"    • {result}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test manual title detection
print("\n📝 Manual title detection test:")
try:
    from app.rules.title_utils import is_title_or_heading
    import spacy
    from bs4 import BeautifulSoup
    
    nlp = spacy.load("en_core_web_sm")
    soup = BeautifulSoup(test_html, "html.parser")
    text_content = soup.get_text()
    doc = nlp(text_content)
    
    for token in doc:
        if token.text.lower() in ['several', 'things'] or token.dep_ == "auxpass":
            sentence = token.sent.text.strip()
            is_title = is_title_or_heading(sentence, test_html)
            print(f"  - Token '{token.text}' | dep: {token.dep_} | Title check: {is_title}")
            if is_title:
                print(f"    → Should be EXCLUDED (but rules found it)")
                
except Exception as e:
    print(f"  ❌ Error: {e}")
