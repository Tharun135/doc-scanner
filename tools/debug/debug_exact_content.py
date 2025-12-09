#!/usr/bin/env python3
"""
Test with the exact content from the main test
"""

import sys
import os
sys.path.append('.')

# Exact content from the main test
test_doc = '''
<h1>User Documentation</h1>
<h2>Getting Started Guide</h2>
<p>Introduction</p>
<p>INSTALLATION REQUIREMENTS</p>
<p>1. Basic Configuration</p>

<p>This regular sentence has several vague things that were written by someone and contains nominalizations like implementation.</p>
'''

print("🔍 Testing with exact main test content...")
print(f"📝 Content:\n{test_doc}\n")

# Test individual rules
print("📝 Testing vague_terms:")
from app.rules.vague_terms import check as vague_check
vague_results = vague_check(test_doc)
print(f"  - Results: {len(vague_results)} issues")
for result in vague_results:
    print(f"    • {result}")

print("\n📝 Testing passive_voice:")
from app.rules.passive_voice import check as passive_check
passive_results = passive_check(test_doc)
print(f"  - Results: {len(passive_results)} issues")
for result in passive_results:
    print(f"    • {result}")

# Analyze with spaCy to understand sentence structure
print("\n🔍 Sentence analysis:")
from bs4 import BeautifulSoup
import spacy
from app.rules.title_utils import is_title_or_heading

nlp = spacy.load("en_core_web_sm")
soup = BeautifulSoup(test_doc, "html.parser")
text_content = soup.get_text()
doc = nlp(text_content)

for i, sent in enumerate(doc.sents):
    sent_text = sent.text.strip()
    is_title = is_title_or_heading(sent_text, test_doc)
    has_vague = any(word in sent_text.lower() for word in ['several', 'things'])
    has_passive = any(token.dep_ == "auxpass" for token in sent)
    
    if has_vague or has_passive:
        print(f"  {i+1}. '{sent_text[:50]}...' -> Title: {is_title} | Vague: {has_vague} | Passive: {has_passive}")
