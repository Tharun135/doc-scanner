#!/usr/bin/env python3
"""
Test the complete modal rule with debug output
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import spacy
from bs4 import BeautifulSoup

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def test_complete_modal_rule():
    """Test the complete modal rule with debug"""
    
    test_sentence = "You can configure the system and you can also modify the settings."
    print(f"Testing sentence: {test_sentence}")
    
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(test_sentence, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule 4: Check for modal verbs that could be simplified
    modal_verbs = ["would", "should", "could", "might", "must", "can"]
    processed_sentences = set()  # Track processed sentences to avoid duplicates
    
    print("\nProcessing modal verbs:")
    
    for token in doc:
        if token.text.lower() in modal_verbs and token.pos_ == "AUX":
            print(f"\nFound modal '{token.text}' at position {token.i}")
            
            # Look for the next verb, skipping adverbs and other intervening words
            verb_token = None
            for i in range(1, min(4, len(doc) - token.i)):  # Look ahead up to 3 tokens
                next_token = token.nbor(i) if token.i + i < len(doc) else None
                if next_token:
                    print(f"  Checking token {token.i + i}: '{next_token.text}' | POS: '{next_token.pos_}'")
                    if next_token.pos_ == "VERB":
                        verb_token = next_token
                        print(f"  Found verb: '{verb_token.text}'")
                        break
                    elif next_token.pos_ in ["PUNCT", "CCONJ", "SCONJ"]:  # Stop at punctuation or conjunctions
                        print(f"  Stopped at punctuation/conjunction: '{next_token.text}'")
                        break
            
            if verb_token:
                sentence = token.sent.text.strip()
                print(f"  Sentence: '{sentence}'")
                
                # Skip if we already processed this sentence for modal verbs
                sentence_key = f"modal_{sentence}"
                print(f"  Sentence key: '{sentence_key}'")
                print(f"  Already processed: {sentence_key in processed_sentences}")
                
                if sentence_key in processed_sentences:
                    print("  SKIPPING - already processed")
                    continue
                
                # Check conditional context
                def _is_conditional_or_hypothetical(sentence):
                    """Check if modal usage is appropriate for conditionals or hypotheticals"""
                    conditional_indicators = ["if", "unless", "suppose", "imagine", "hypothetically", "potentially", "possibly"]
                    return any(indicator in sentence.lower() for indicator in conditional_indicators)
                
                is_conditional = _is_conditional_or_hypothetical(sentence)
                print(f"  Is conditional: {is_conditional}")
                    
                if not is_conditional:
                    print("  Processing for suggestion...")
                    # Find the first modal verb in the sentence for the rewrite
                    first_modal = None
                    first_verb = None
                    
                    for sent_token in token.sent:
                        if (sent_token.text.lower() in modal_verbs and 
                            sent_token.pos_ == "AUX"):
                            print(f"    Checking sent_token '{sent_token.text}' at {sent_token.i}")
                            # Look for the next verb after this modal
                            for j in range(1, min(4, len(doc) - sent_token.i)):
                                next_sent_token = sent_token.nbor(j) if sent_token.i + j < len(doc) else None
                                if next_sent_token:
                                    print(f"      Checking {sent_token.i + j}: '{next_sent_token.text}' | POS: '{next_sent_token.pos_}'")
                                    if next_sent_token.pos_ == "VERB":
                                        first_modal = sent_token.text
                                        first_verb = next_sent_token.text
                                        print(f"      Found first modal+verb: '{first_modal}' + '{first_verb}'")
                                        break
                                    elif next_sent_token.pos_ in ["PUNCT", "CCONJ", "SCONJ"]:
                                        print(f"      Stopped at: '{next_sent_token.text}'")
                                        break
                            if first_modal and first_verb:
                                break
                    
                    if first_modal and first_verb:
                        print(f"  ADDING SUGGESTION with '{first_modal}' + '{first_verb}'")
                        suggestions.append(f"Consider rewriting to describe the action instead of using '{first_modal.lower()}'. Original: \"{sentence}\" → Suggested: \"Mock rewrite\"")
                        processed_sentences.add(sentence_key)  # Mark as processed
                        print(f"  Marked as processed: {sentence_key}")
                    else:
                        print("  No valid first modal+verb found")
                else:
                    print("  SKIPPING - conditional sentence")
            else:
                print("  No verb found for this modal")
    
    print(f"\nFinal suggestions: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"Suggestion {i}: {suggestion}")

if __name__ == "__main__":
    test_complete_modal_rule()
