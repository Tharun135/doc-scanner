#!/usr/bin/env python3
"""Test full document processing with just "The" to reproduce the issue."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import get_spacy_model, review_document, get_rules

def test_document_processing():
    """Test how the document processing handles edge cases."""
    
    test_cases = [
        "The",
        "The.",
        "The document",
        "The document.",
        "The document is written.",
        "The document is written by the author."
    ]
    
    print("🔬 TESTING FULL DOCUMENT PROCESSING")
    print("=" * 50)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n{i}. Testing document: {repr(test_text)}")
        
        try:
            # Test spaCy sentence splitting
            spacy_nlp = get_spacy_model()
            if spacy_nlp:
                doc = spacy_nlp(test_text)
                sentences = list(doc.sents)
                print(f"   spaCy found {len(sentences)} sentences:")
                for j, sent in enumerate(sentences, 1):
                    plain_sentence = sent.text.strip()
                    print(f"     {j}. {repr(plain_sentence)} (len={len(plain_sentence)})")
                    
                    # Check filtering condition
                    passes_filter = len(plain_sentence) > 3 and not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence)
                    print(f"        Passes filter: {passes_filter}")
            
            # Test full document analysis
            print(f"   Full document analysis:")
            result = review_document(test_text, get_rules())
            issues = result.get('issues', [])
            print(f"     Found {len(issues)} issues:")
            
            for j, issue in enumerate(issues, 1):
                print(f"     Issue {j}: {issue.get('message', 'N/A')}")
                print(f"       Text: {repr(issue.get('text', 'N/A'))}")
                print(f"       Rule: {issue.get('rule', 'N/A')}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    import re
    test_document_processing()
