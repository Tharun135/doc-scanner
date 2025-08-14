#!/usr/bin/env python3
"""
Simple test to debug the upload error.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sentence_extraction():
    """Test the sentence extraction function directly."""
    
    try:
        from app.app import extract_sentences_from_html
        
        test_html = "<p>This is a simple sentence. This is another one.</p>"
        
        print("Testing sentence extraction...")
        print(f"Input HTML: {test_html}")
        
        result = extract_sentences_from_html(test_html)
        
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        if result:
            for i, sent in enumerate(result):
                print(f"Sentence {i}: {sent}")
                print(f"  Type: {type(sent)}")
                if isinstance(sent, dict):
                    print(f"  Keys: {sent.keys()}")
                    print(f"  Plain text: {sent.get('plain_text', 'MISSING')}")
                    print(f"  HTML context: {sent.get('html_context', 'MISSING')}")
        
        print("✅ Sentence extraction test completed")
        
    except Exception as e:
        print(f"❌ Error in sentence extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sentence_extraction()
