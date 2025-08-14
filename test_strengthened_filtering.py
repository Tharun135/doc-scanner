#!/usr/bin/env python3
"""Test the strengthened sentence filtering to prevent short fragments."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import get_spacy_model
import re

def test_strengthened_filtering():
    """Test the new filtering logic to ensure short fragments are blocked."""
    
    print("🛡️ TESTING STRENGTHENED SENTENCE FILTERING")
    print("=" * 50)
    
    # Test cases that should be filtered out
    should_filter_out = [
        "The",
        "The.",
        "It is",
        "Was done", 
        "Is ready",
        "The end",
        "To be",
        "Not done"
    ]
    
    # Test cases that should pass through
    should_pass_through = [
        "The document is complete",
        "The quick brown fox jumps",
        "This sentence is long enough",
        "The document is written by John",
        "It was a beautiful day yesterday"
    ]
    
    print("1. Testing cases that SHOULD BE FILTERED OUT:")
    print("-" * 45)
    
    spacy_nlp = get_spacy_model()
    
    for i, test_text in enumerate(should_filter_out, 1):
        print(f"{i}. '{test_text}' ... ", end="")
        
        # Test the new filtering logic
        plain_sentence = re.sub(r'\s+', ' ', test_text.strip())
        
        passes_filter = (len(plain_sentence) > 8 and 
                        not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                        len(plain_sentence.split()) >= 2)
        
        if not passes_filter:
            print("✅ FILTERED OUT (correct)")
        else:
            print("❌ PASSED THROUGH (incorrect)")
            print(f"    Length: {len(plain_sentence)}, Words: {len(plain_sentence.split())}")
    
    print(f"\n2. Testing cases that SHOULD PASS THROUGH:")
    print("-" * 45)
    
    for i, test_text in enumerate(should_pass_through, 1):
        print(f"{i}. '{test_text}' ... ", end="")
        
        # Test the new filtering logic
        plain_sentence = re.sub(r'\s+', ' ', test_text.strip())
        
        passes_filter = (len(plain_sentence) > 8 and 
                        not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                        len(plain_sentence.split()) >= 2)
        
        if passes_filter:
            print("✅ PASSED THROUGH (correct)")
        else:
            print("❌ FILTERED OUT (incorrect)")
            print(f"    Length: {len(plain_sentence)}, Words: {len(plain_sentence.split())}")

def test_spacy_sentence_splitting():
    """Test how spaCy splits sentences with the new filtering."""
    
    print(f"\n\n🔬 TESTING SPACY SENTENCE SPLITTING WITH NEW FILTERING")
    print("=" * 60)
    
    test_documents = [
        "The document is written. The end.",
        "The quick brown fox. The cat sleeps.",
        "The. Document follows after.",
        "Title: The Document\n\nThe content follows here.",
    ]
    
    spacy_nlp = get_spacy_model()
    if spacy_nlp:
        for i, test_doc in enumerate(test_documents, 1):
            print(f"\n{i}. Document: {repr(test_doc)}")
            doc = spacy_nlp(test_doc)
            sentences = list(doc.sents)
            print(f"   spaCy found {len(sentences)} sentences:")
            
            filtered_count = 0
            for j, sent in enumerate(sentences, 1):
                plain_sentence = re.sub(r'\s+', ' ', sent.text.strip())
                
                passes_filter = (len(plain_sentence) > 8 and 
                               not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                               len(plain_sentence.split()) >= 2)
                
                status = "PASSED" if passes_filter else "FILTERED"
                if passes_filter:
                    filtered_count += 1
                
                print(f"     {j}. {repr(plain_sentence)} -> {status}")
                print(f"        Length: {len(plain_sentence)}, Words: {len(plain_sentence.split())}")
            
            print(f"   Result: {filtered_count} sentences would be processed")

if __name__ == "__main__":
    test_strengthened_filtering()
    test_spacy_sentence_splitting()
