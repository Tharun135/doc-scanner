#!/usr/bin/env python3
"""
Check what the remaining 2 issues are about
"""

import sys
import os
sys.path.append('.')

test_doc = '''
<h1>User Documentation</h1>
<h2>Getting Started Guide</h2>
<p>Introduction</p>
<p>INSTALLATION REQUIREMENTS</p>
<p>1. Basic Configuration</p>

<p>This regular sentence has several vague things that were written by someone and contains nominalizations like implementation.</p>
'''

print("🔍 Checking remaining issues...")

# Test readability_rules
print("\n📝 Testing readability_rules:")
from app.rules.readability_rules import check as readability_check
readability_results = readability_check(test_doc)
print(f"  - Results: {len(readability_results)} issues")
for result in readability_results:
    print(f"    • {result}")

# Test style_rules
print("\n📝 Testing style_rules:")
from app.rules.style_rules import check as style_check
style_results = style_check(test_doc)
print(f"  - Results: {len(style_results)} issues")
for result in style_results:
    print(f"    • {result}")

# Check if "INSTALLATION REQUIREMENTS" should be excluded as title
print("\n📝 Testing title detection for ALL CAPS:")
from app.rules.title_utils import is_title_or_heading
caps_result = is_title_or_heading("INSTALLATION REQUIREMENTS", test_doc)
print(f"  - 'INSTALLATION REQUIREMENTS' is title: {caps_result}")

# Test if the rule is checking sentences that contain titles
print("\n📝 Analyzing sentence processing:")
import spacy
from bs4 import BeautifulSoup
nlp = spacy.load("en_core_web_sm")
soup = BeautifulSoup(test_doc, "html.parser")
text_content = soup.get_text()
doc = nlp(text_content)

for i, sent in enumerate(doc.sents):
    sent_text = sent.text.strip()
    is_title = is_title_or_heading(sent_text, test_doc)
    has_caps = any(word.isupper() and len(word) > 1 for word in sent_text.split())
    
    if has_caps:
        print(f"  {i+1}. '{sent_text[:50]}...' -> Title: {is_title} | Has CAPS: {has_caps}")

print(f"\n📝 Individual words check:")
for token in doc:
    if token.text == "INSTALLATION" or token.text == "REQUIREMENTS":
        sent_text = token.sent.text.strip()
        is_title = is_title_or_heading(sent_text, test_doc)
        print(f"  - Token '{token.text}' in sentence: '{sent_text[:30]}...' | Title: {is_title}")
