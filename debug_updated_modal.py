#!/usr/bin/env python3
"""
Test script to verify the updated modal verb rule with lookahead
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import spacy
from bs4 import BeautifulSoup

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def debug_updated_modal_rule():
    """Test the updated modal verb detection with lookahead"""
    
    test_sentence = "You can also modify the settings."
    print(f"Testing sentence: {test_sentence}")
    
    # Strip HTML tags from content
    soup = BeautifulSoup(test_sentence, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    modal_verbs = ["would", "should", "could", "might", "must", "can"]
    print("\nUpdated modal verb detection:")
    
    for token in doc:
        if token.text.lower() in modal_verbs and token.pos_ == "AUX":
            print(f"Found modal '{token.text}' at position {token.i}")
            
            # Look for the next verb, skipping adverbs and other intervening words
            verb_token = None
            for i in range(1, min(4, len(doc) - token.i)):  # Look ahead up to 3 tokens
                next_token = token.nbor(i) if token.i + i < len(doc) else None
                if next_token:
                    print(f"  Looking at token {token.i + i}: '{next_token.text}' | POS: '{next_token.pos_}'")
                    if next_token.pos_ == "VERB":
                        verb_token = next_token
                        print(f"  Found verb: '{verb_token.text}'")
                        break
                    elif next_token.pos_ in ["PUNCT", "CCONJ", "SCONJ"]:  # Stop at punctuation or conjunctions
                        print(f"  Stopped at punctuation/conjunction: '{next_token.text}'")
                        break
            
            if verb_token:
                print(f"  Result: Modal '{token.text}' + Verb '{verb_token.text}' - VALID")
            else:
                print(f"  Result: No verb found - INVALID")

if __name__ == "__main__":
    debug_updated_modal_rule()
