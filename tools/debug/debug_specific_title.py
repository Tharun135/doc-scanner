#!/usr/bin/env python3
"""
Debug the specific title issue: "Generating the connector configuration"
"""

import sys
import os
sys.path.append('.')

# Test with the specific content that's causing issues
test_content = """
<h2>Generating the connector configuration</h2>
<p>This is some regular content that should be checked.</p>
"""

print("🔍 Debugging specific title issue...")
print(f"📝 Test content:\n{test_content}\n")

# Test title detection
from app.rules.title_utils import is_title_or_heading
title_result = is_title_or_heading("Generating the connector configuration", test_content)
print(f"📊 Title detection result: {title_result}")

# Test with spaCy processing
import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")
soup = BeautifulSoup(test_content, "html.parser")
text_content = soup.get_text()
doc = nlp(text_content)

print(f"📄 Extracted text: '{text_content}'\n")

print("🔍 Sentence analysis:")
for i, sent in enumerate(doc.sents):
    sent_text = sent.text.strip()
    is_title = is_title_or_heading(sent_text, test_content)
    print(f"  {i+1}. '{sent_text}' -> Title: {is_title}")

# Test the specific rules that are flagging this
print("\n📝 Testing nominalizations rule:")
from app.rules.nominalizations import check as nom_check
nom_results = nom_check(test_content)
print(f"  - Results: {len(nom_results)} issues")
for result in nom_results:
    print(f"    • {result}")

print("\n📝 Testing readability rule:")
from app.rules.readability_rules import check as read_check
read_results = read_check(test_content)
print(f"  - Results: {len(read_results)} issues")
for result in read_results:
    print(f"    • {result}")

# Check token-level analysis
print("\n🔍 Token analysis for 'configuration':")
for token in doc:
    if token.text.lower() == "configuration":
        sent_text = token.sent.text.strip()
        is_title = is_title_or_heading(sent_text, test_content)
        print(f"  - Token: '{token.text}' | Sentence: '{sent_text}' | Title: {is_title}")
        print(f"  - Token POS: {token.pos_} | Lemma: {token.lemma_}")

# Check if our title detection patterns are working
import re
test_phrase = "Generating the connector configuration"
print(f"\n🔍 Pattern analysis for '{test_phrase}':")
print(f"  - Starts with 'generating': {test_phrase.lower().startswith('generating')}")
print(f"  - Contains 'configuration': {'configuration' in test_phrase.lower()}")
print(f"  - Length: {len(test_phrase.split())} words")
print(f"  - Title case: {test_phrase.istitle()}")
print(f"  - Ends with punctuation: {test_phrase.endswith(('.', '!', '?', ';', ':'))}")

# Check if it's being detected as HTML heading
soup_check = BeautifulSoup(test_content, "html.parser")
headings = soup_check.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
print(f"  - Found in HTML headings: {any(test_phrase in h.get_text().strip() for h in headings)}")

# Test individual heading content
for h in headings:
    h_text = h.get_text().strip()
    print(f"  - Heading text: '{h_text}' | Matches: {h_text == test_phrase}")
