#!/usr/bin/env python3
"""
Debug the specific sentence that's not being rewritten properly.
"""

import app.rules.passive_voice as passive_voice
import spacy

# Load spaCy for debugging
nlp = spacy.load("en_core_web_sm")

def debug_sentence():
    """Debug the specific problematic sentence."""
    
    sentence = "This tool is needed to convert vendor and device specific configuration files to the standardized Connectivity-Suite compatible configurations."
    
    print("=== Debugging Passive Voice Detection ===\n")
    print(f"Sentence: {sentence}")
    print("\n" + "="*60)
    
    # Analyze with spaCy
    doc = nlp(sentence)
    sent = list(doc.sents)[0]
    
    print("SpaCy Analysis:")
    for token in sent:
        print(f"  {token.text:15} | {token.dep_:12} | {token.tag_:8} | {token.pos_}")
    
    print("\n" + "="*60)
    
    # Check what our current rule detects
    suggestions = passive_voice.check(sentence)
    
    print("Current Rule Output:")
    if suggestions:
        for suggestion in suggestions:
            print(suggestion)
    else:
        print("No passive voice detected")
    
    print("\n" + "="*60)
    
    # Check for auxpass specifically
    has_auxpass = any(token.dep_ == "auxpass" for token in sent)
    print(f"Has auxpass dependency: {has_auxpass}")
    
    # Check for other passive indicators
    passive_indicators = []
    for token in sent:
        if token.dep_ == "auxpass":
            passive_indicators.append(f"auxpass: {token.text}")
        elif token.dep_ == "nsubjpass":
            passive_indicators.append(f"nsubjpass: {token.text}")
        elif token.tag_ == "VBN" and token.dep_ == "ROOT":
            passive_indicators.append(f"past participle root: {token.text}")
    
    print(f"Passive indicators found: {passive_indicators}")

if __name__ == "__main__":
    debug_sentence()
