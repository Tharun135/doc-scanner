#!/usr/bin/env python3
"""Debug the exact sentence processing issue to find where 'The' comes from."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import get_spacy_model
from app.rules.passive_voice import check as check_passive_voice
from app.rules.passive_voice import _emergency_passive_detection

def debug_sentence_processing():
    """Debug how sentences are being processed and where 'The' comes from."""
    
    print("🕵️ DEBUGGING SENTENCE PROCESSING ISSUE")
    print("=" * 60)
    
    # Test with various inputs that might produce "The" as a sentence
    test_documents = [
        "The document is complete.",
        "The document is written by John.",
        "The quick brown fox jumps. The document is written.",
        "This is a test. The end.",
        "The",  # Direct test
        "The.",  # With period
        "The document",  # Without period
        "The document is written",  # Passive voice without period
    ]
    
    for i, test_doc in enumerate(test_documents, 1):
        print(f"\n{i}. Testing document: {repr(test_doc)}")
        print("-" * 40)
        
        # Test spaCy sentence splitting
        spacy_nlp = get_spacy_model()
        if spacy_nlp:
            doc = spacy_nlp(test_doc)
            sentences = list(doc.sents)
            print(f"   spaCy sentences ({len(sentences)}):")
            for j, sent in enumerate(sentences, 1):
                plain_sentence = sent.text.strip()
                print(f"     {j}. {repr(plain_sentence)} (len={len(plain_sentence)})")
                
                # Check if it would pass the filter
                passes_filter = len(plain_sentence) > 3 and not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence)
                print(f"        Passes sentence filter: {passes_filter}")
                
                # Test passive voice on this sentence
                if passes_filter:
                    try:
                        passive_result = check_passive_voice(plain_sentence)
                        print(f"        Passive voice result: {len(passive_result)} issues")
                        for issue in passive_result:
                            print(f"          - {issue.get('message', 'N/A')}")
                            print(f"            Text: {repr(issue.get('text', 'N/A'))}")
                    except Exception as e:
                        print(f"        Passive voice error: {e}")
        
        # Test emergency fallback directly
        print(f"   Emergency fallback test:")
        try:
            emergency_result = _emergency_passive_detection(test_doc)
            print(f"     Found {len(emergency_result)} issues:")
            for issue in emergency_result:
                print(f"       - {issue.get('message', 'N/A')}")
                print(f"         Text: {repr(issue.get('text', 'N/A'))}")
        except Exception as e:
            print(f"     Emergency fallback error: {e}")

def test_sentence_splitting_edge_cases():
    """Test edge cases in sentence splitting that might create 'The'."""
    
    print(f"\n\n🔬 TESTING SENTENCE SPLITTING EDGE CASES")
    print("=" * 50)
    
    edge_cases = [
        "The document is written. The end.",
        "The.\nDocument follows.",
        "The document\nis written here.",
        "Title: The Document\n\nThe content follows.",
        "- The item\n- Another item",
        "1. The first point\n2. The second point"
    ]
    
    spacy_nlp = get_spacy_model()
    if spacy_nlp:
        for i, text in enumerate(edge_cases, 1):
            print(f"\n{i}. Text: {repr(text)}")
            doc = spacy_nlp(text)
            sentences = list(doc.sents)
            print(f"   Sentences found: {len(sentences)}")
            for j, sent in enumerate(sentences, 1):
                sentence_text = sent.text.strip()
                print(f"     {j}. {repr(sentence_text)} (len={len(sentence_text)})")

if __name__ == "__main__":
    import re
    debug_sentence_processing()
    test_sentence_splitting_edge_cases()
