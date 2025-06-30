#!/usr/bin/env python3
"""
Debug spaCy token analysis for apostrophe detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import spacy
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")

def debug_sentence(text):
    print(f"\nAnalyzing: {text}")
    print("-" * 50)
    
    # Strip HTML tags from content
    soup = BeautifulSoup(text, "html.parser")
    text_content = soup.get_text()
    
    doc = nlp(text_content)
    
    for sent in doc.sents:
        print(f"Sentence: {sent.text}")
        print("Tokens:")
        for i, token in enumerate(sent):
            if "'s" in token.text:
                print(f"  {i}: '{token.text}' | POS: {token.pos_} | Tag: {token.tag_} | Dep: {token.dep_} | Head: {token.head.text}")
                
                # Check surrounding tokens
                prev_token = sent[i - 1] if i > 0 else None
                next_token = sent[i + 1] if i + 1 < len(sent) else None
                
                if prev_token:
                    print(f"    Previous: '{prev_token.text}' | POS: {prev_token.pos_}")
                if next_token:
                    print(f"    Next: '{next_token.text}' | POS: {next_token.pos_}")
            else:
                print(f"  {i}: '{token.text}' | POS: {token.pos_} | Tag: {token.tag_} | Dep: {token.dep_}")

# Test cases
test_cases = [
    "The API's are down.",                    # Should be plural
    "Tharun's laptop is working.",           # Should be possessive
    "All CPU's are working fine.",           # Should be plural
    "The server's CPU is overheating.",      # Should be possessive
]

for test_case in test_cases:
    debug_sentence(test_case)
