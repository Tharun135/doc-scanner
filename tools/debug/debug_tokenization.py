#!/usr/bin/env python3
"""
Debug script to understand sentence tokenization behavior
"""

import sys
import os
import spacy

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

def debug_sentence_tokenization():
    """Debug how spaCy tokenizes different types of text"""
    
    nlp = spacy.load("en_core_web_sm")
    
    test_texts = [
        "ie/d/j/simatic/v1/slmp1/dp/r//default",
        "this sentence should start with capital",
        "The API endpoint is api/v1/users but this sentence needs capital",
        "We use config.json for settings and this also needs capital",
    ]
    
    print("Debugging sentence tokenization...")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\nInput: '{text}'")
        doc = nlp(text)
        
        print(f"Number of sentences: {len(list(doc.sents))}")
        for i, sent in enumerate(doc.sents):
            print(f"  Sentence {i+1}: '{sent.text.strip()}'")
            print(f"    First char: '{sent.text[0] if sent.text else 'EMPTY'}'")
            print(f"    Is lowercase: {sent.text[0].islower() if sent.text else False}")

if __name__ == "__main__":
    debug_sentence_tokenization()
