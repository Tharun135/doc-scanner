#!/usr/bin/env python3
"""
Debug script to understand why multi-modal sentences aren't being detected
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import spacy
from bs4 import BeautifulSoup

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def debug_modal_detection():
    """Debug modal verb detection"""
    
    test_sentence = "You can configure the system and you can also modify the settings."
    print(f"Testing sentence: {test_sentence}")
    
    # Strip HTML tags from content
    soup = BeautifulSoup(test_sentence, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    print("\nToken analysis:")
    for i, token in enumerate(doc):
        print(f"Token {i}: '{token.text}' | Lemma: '{token.lemma_}' | POS: '{token.pos_}' | Tag: '{token.tag_}' | Dep: '{token.dep_}'")
    
    print("\nSentence analysis:")
    for sent in doc.sents:
        print(f"Sentence: '{sent.text}'")
    
    # Check for modal verbs
    modal_verbs = ["would", "should", "could", "might", "must", "can"]
    print("\nModal verb detection:")
    
    for token in doc:
        if token.text.lower() in modal_verbs:
            print(f"Found modal '{token.text}' at position {token.i}")
            print(f"  POS: {token.pos_}")
            print(f"  Is AUX: {token.pos_ == 'AUX'}")
            
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token:
                print(f"  Next token: '{next_token.text}' | POS: '{next_token.pos_}'")
                print(f"  Next is VERB: {next_token.pos_ == 'VERB'}")
            else:
                print(f"  No next token")

if __name__ == "__main__":
    debug_modal_detection()
