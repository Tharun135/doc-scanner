#!/usr/bin/env python3
"""
Debug title exclusion to understand what sentences are being processed
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app.rules.title_utils import is_title_or_heading
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Test content
test_html = """<h2>Basic Configuration</h2>
<p>This rule checks for several things in your document. You should avoid passive voice construction when possible. The implementation must be done carefully.</p>"""

print("🔍 Debugging title exclusion...")
print(f"📝 Test HTML:\n{test_html}\n")

# Process with spaCy
from bs4 import BeautifulSoup
soup = BeautifulSoup(test_html, "html.parser")
text_content = soup.get_text()
doc = nlp(text_content)

print(f"📄 Extracted text: '{text_content}'\n")

print("🔍 Sentence analysis:")
for i, sent in enumerate(doc.sents):
    sent_text = sent.text.strip()
    is_title = is_title_or_heading(sent_text, test_html)
    print(f"  {i+1}. '{sent_text}' -> Title: {is_title}")

print("\n🔍 Token analysis:")
for token in doc:
    sent_text = token.sent.text.strip()
    is_title = is_title_or_heading(sent_text, test_html)
    if token.text.lower() in ['basic', 'configuration', 'several', 'things', 'implementation'] or token.dep_ == "auxpass":
        print(f"  Token: '{token.text}' | Sentence: '{sent_text[:50]}...' | Title: {is_title}")

print(f"\n📊 Testing individual components:")
print(f"  - 'Basic Configuration' -> {is_title_or_heading('Basic Configuration', test_html)}")
print(f"  - 'Basic Configuration This rule checks...' -> {is_title_or_heading('Basic Configuration This rule checks for several things in your document.', test_html)}")
