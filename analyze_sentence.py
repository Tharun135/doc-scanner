#!/usr/bin/env python3
"""
Analyze the specific sentence tokenization issue
"""

import sys
import os
import spacy

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

def analyze_problematic_sentence():
    """Analyze the problematic sentence"""
    
    nlp = spacy.load("en_core_web_sm")
    
    full_text = "ts: timestamp of the data point. it is in ISO 8601 Zulu format."
    
    print("Analyzing sentence tokenization...")
    print("=" * 50)
    print(f"Full text: '{full_text}'")
    
    doc = nlp(full_text)
    
    print(f"\nNumber of sentences: {len(list(doc.sents))}")
    for i, sent in enumerate(doc.sents):
        print(f"  Sentence {i+1}: '{sent.text.strip()}'")
        print(f"    First char: '{sent.text[0] if sent.text else 'EMPTY'}'")
        print(f"    Is lowercase: {sent.text[0].islower() if sent.text else False}")
        print(f"    Should be flagged: {'YES' if sent.text[0].islower() and not sent.text.startswith('ts:') else 'NO'}")

if __name__ == "__main__":
    analyze_problematic_sentence()
