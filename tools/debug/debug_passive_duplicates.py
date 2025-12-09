#!/usr/bin/env python3

import sys
sys.path.append('.')
import spacy

# Debug the duplicate issue
test_content = "Normal text that was written in passive voice should be flagged."

nlp = spacy.load("en_core_web_sm")
doc = nlp(test_content)

print("=== PASSIVE VOICE TOKEN ANALYSIS ===")
print(f"Content: {test_content}")
print(f"Sentences: {len(list(doc.sents))}")

passive_tokens = []
for token in doc:
    if token.dep_ == "auxpass":
        passive_tokens.append({
            'token': token.text,
            'sentence': token.sent.text.strip(),
            'dep': token.dep_
        })

print(f"\nPassive tokens found: {len(passive_tokens)}")
for i, info in enumerate(passive_tokens):
    print(f"  {i}: '{info['token']}' in sentence: '{info['sentence']}'")
