#!/usr/bin/env python3

import spacy
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rules.simple_present_tense import check

def debug_sentence(sentence):
    print(f"Testing: {sentence}")
    print("-" * 50)
    
    # Load spaCy model
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(sentence)
    
    # Debug token analysis
    for token in doc:
        print(f'Token: "{token.text}" | Lemma: "{token.lemma_}" | POS: {token.pos_} | Tag: {token.tag_} | Dep: {token.dep_}')
    
    print('\n--- Rule Analysis ---')
    violations = check(sentence)
    print(f'Violations found: {len(violations)}')
    for v in violations:
        print(f'  {v}')
    print()

if __name__ == "__main__":
    # Test the case that should be flagged but isn't
    debug_sentence("The system is processing the data every hour.")
    
    # Test our fixed case
    debug_sentence("Open the Edge Devices window In IEM and select the IED where the EtherNet/IP IO Connector is running.")
