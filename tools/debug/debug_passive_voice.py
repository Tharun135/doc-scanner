#!/usr/bin/env python3

import sys
sys.path.append('.')
import re
import spacy

# Test content
test_content = '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.'

nlp = spacy.load("en_core_web_sm")
doc = nlp(test_content)

print("=== SPACY SENTENCE ANALYSIS ===")
print(f"Original content: {repr(test_content)}")
print(f"Number of sentences spaCy found: {len(list(doc.sents))}")
print()

for i, sent in enumerate(doc.sents):
    print(f"Sentence {i}: {repr(sent.text)}")
    print(f"Sentence {i} stripped: {repr(sent.text.strip())}")
    
    # Test admonition pattern
    admonition_pattern = r'^\s*!!!\s+\w+(?:\s+"[^"]*")?\s*.*$'
    matches = re.match(admonition_pattern, sent.text.strip(), re.IGNORECASE)
    print(f"Admonition pattern matches: {bool(matches)}")
    
    # Check for passive voice tokens in this sentence
    passive_tokens = []
    for token in sent:
        if token.dep_ == "auxpass":
            passive_tokens.append(f"'{token.text}' (dep: {token.dep_})")
    
    print(f"Passive voice tokens: {passive_tokens}")
    print()
