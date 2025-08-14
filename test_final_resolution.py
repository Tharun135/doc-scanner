#!/usr/bin/env python3
"""Final test to confirm the 'The' passive voice issue is completely resolved."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import review_document, get_rules

def test_final_passive_voice_resolution():
    """Final test to confirm the issue is completely resolved."""
    
    print("🎯 FINAL PASSIVE VOICE ISSUE RESOLUTION TEST")
    print("=" * 60)
    
    # Test documents that might previously have caused issues
    test_documents = [
        "The document is written by John.",
        "The quick brown fox jumps. The end.",
        "The document is complete. The task is done.",
        "This is a test document. The document is written by the author.",
        "The. Document follows.",  # Edge case that might create "The"
        "Title: The Document\n\nThe content is written here."
    ]
    
    for i, test_doc in enumerate(test_documents, 1):
        print(f"\n{i}. Testing document: {repr(test_doc)}")
        print("-" * 50)
        
        try:
            # Run full document analysis
            result = review_document(test_doc, get_rules())
            issues = result.get('issues', [])
            
            # Look specifically for passive voice issues
            passive_issues = [issue for issue in issues if 'passive' in issue.get('message', '').lower()]
            
            print(f"   Total issues: {len(issues)}")
            print(f"   Passive voice issues: {len(passive_issues)}")
            
            # Check each passive voice issue
            problematic_issues = []
            for issue in passive_issues:
                text_field = issue.get('text', '')
                print(f"   - Passive issue text: {repr(text_field)} (len={len(text_field)})")
                
                # Flag any suspiciously short text
                if len(text_field) <= 5:
                    problematic_issues.append(issue)
                    print(f"     ⚠️  WARNING: Text too short!")
            
            if len(problematic_issues) == 0:
                print(f"   ✅ SUCCESS: No problematic short passive voice issues")
            else:
                print(f"   ❌ FAILURE: Found {len(problematic_issues)} problematic issues")
                
        except Exception as e:
            print(f"   ERROR: {e}")

def test_sentence_processing_pipeline():
    """Test the sentence processing pipeline directly."""
    
    print(f"\n\n🔧 TESTING SENTENCE PROCESSING PIPELINE")
    print("=" * 50)
    
    from app.app import get_spacy_model
    import re
    
    # Test a document that might create edge cases
    test_text = "The document is written by John. The end."
    print(f"Test text: {repr(test_text)}")
    
    # Simulate the sentence processing logic
    spacy_nlp = get_spacy_model()
    if spacy_nlp:
        doc = spacy_nlp(test_text)
        
        processed_sentences = []
        for sent in doc.sents:
            plain_sentence = re.sub(r'\s+', ' ', sent.text.strip())
            
            # Apply the new filtering logic
            if (len(plain_sentence) > 8 and 
                not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                len(plain_sentence.split()) >= 2):
                
                processed_sentences.append(plain_sentence)
                print(f"   ✅ Sentence processed: {repr(plain_sentence)}")
            else:
                print(f"   🚫 Sentence filtered: {repr(plain_sentence)} (len={len(plain_sentence)}, words={len(plain_sentence.split())})")
        
        print(f"\n   Final result: {len(processed_sentences)} sentences will be analyzed")
        
        # Test passive voice on each processed sentence
        from app.rules.passive_voice import check as check_passive_voice
        
        for i, sentence in enumerate(processed_sentences, 1):
            print(f"\n   Testing sentence {i} for passive voice: {repr(sentence)}")
            try:
                passive_issues = check_passive_voice(sentence)
                print(f"     Found {len(passive_issues)} passive voice issues")
                for issue in passive_issues:
                    text_field = issue.get('text', '')
                    print(f"       Issue text: {repr(text_field)}")
            except Exception as e:
                print(f"     Error: {e}")

if __name__ == "__main__":
    test_final_passive_voice_resolution()
    test_sentence_processing_pipeline()
