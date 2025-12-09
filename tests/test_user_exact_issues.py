#!/usr/bin/env python3
"""
Test the exact issues the user reported:
- Nominalizations flagging 'configuration' in titles
- Readability flagging titles with high grade level
"""

import sys
import os
sys.path.append('.')

print("🔍 Testing exact user-reported issues...")

# Create content that would trigger the exact issues mentioned
test_content = '''<h1>Generating the connector configuration</h1>
<p>This is a simple sentence to test.</p>'''

print(f"📝 Test content:\n{test_content}\n")

# Force reload modules to ensure we get the latest changes
print("🔄 Reloading modules...")
import importlib

# Import and reload all relevant modules
import app.rules.nominalizations
import app.rules.readability_rules  
import app.rules.title_utils

importlib.reload(app.rules.title_utils)
importlib.reload(app.rules.nominalizations)
importlib.reload(app.rules.readability_rules)

print("✅ Modules reloaded")

# Test the issues
print("\n📝 Testing nominalizations (should find 0 issues):")
nom_results = app.rules.nominalizations.check(test_content)
print(f"  - Found {len(nom_results)} issues:")
for result in nom_results:
    print(f"    • {result}")

print("\n📝 Testing readability (should find 0 issues):")
read_results = app.rules.readability_rules.check(test_content)  
print(f"  - Found {len(read_results)} issues:")
for result in read_results:
    print(f"    • {result}")

# Test title detection directly
print(f"\n📝 Title detection test:")
title_result = app.rules.title_utils.is_title_or_heading("Generating the connector configuration", test_content)
print(f"  - 'Generating the connector configuration' detected as title: {title_result}")

# Debug spaCy processing
print(f"\n🔍 spaCy sentence analysis:")
import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")
soup = BeautifulSoup(test_content, "html.parser")
text_content = soup.get_text()
doc = nlp(text_content)

for i, sent in enumerate(doc.sents):
    sent_text = sent.text.strip()
    is_title = app.rules.title_utils.is_title_or_heading(sent_text, test_content)
    print(f"  Sentence {i+1}: '{sent_text[:50]}...' -> Title: {is_title}")
    
    # Check for nominalization tokens in this sentence
    for token in sent:
        if token.text.lower() == 'configuration':
            print(f"    - Found 'configuration' token | POS: {token.pos_} | Should be excluded: {is_title}")

print(f"\n✅ If you're still seeing issues, please:")
print(f"   1. Restart your application to reload the rules")
print(f"   2. Check if your content structure is different")
print(f"   3. Verify the exact text that's being flagged")
