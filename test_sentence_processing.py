#!/usr/bin/env python3

"""
Test the sentence processing logic directly without server
"""

import sys
import os

# Add the app directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app import get_spacy_model
    import re
    from bs4 import BeautifulSoup
    
    def test_sentence_processing():
        print("🔍 TESTING SENTENCE PROCESSING LOGIC DIRECTLY")
        print("=" * 55)
        
        # Test HTML content similar to what causes issues
        html_content = """<p>Security guidelines for usage of USB sticks within shop floor are applied.
The system uses appropriate security measures.
Customer is responsible for configuring the application security settings.</p>"""
        
        print("📝 Input HTML:")
        print(html_content)
        
        # Parse with BeautifulSoup like the app does
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content like the app does
        plain_text = soup.get_text()
        print(f"\n📝 Plain text extracted:")
        print(f"'{plain_text}'")
        
        # Process paragraph blocks
        paragraph_blocks = []
        
        for element in soup.find_all(['p', 'div']):
            block_text = element.get_text().strip()
            if block_text and len(block_text) > 10:
                paragraph_blocks.append({
                    'plain': block_text,
                    'html': str(element)
                })
        
        print(f"\n📦 Found {len(paragraph_blocks)} paragraph blocks:")
        for i, block in enumerate(paragraph_blocks, 1):
            print(f"  Block {i}: '{block['plain'][:80]}...'")
        
        # Process sentences like the app does
        sentences = []
        
        spacy_nlp = get_spacy_model()
        if spacy_nlp:
            print(f"\n🔍 Processing with spaCy...")
            
            for block_data in paragraph_blocks:
                plain_block = block_data['plain']
                html_block = block_data['html']
                
                doc = spacy_nlp(plain_block)
                
                for sent in doc.sents:
                    plain_sentence = re.sub(r'\s+', ' ', sent.text.strip())
                    
                    if (len(plain_sentence) > 8 and 
                        not re.match(r'^[.!?,:;\s\-_]*$', plain_sentence) and
                        len(plain_sentence.split()) >= 2):
                        
                        # FIXED: Create individual sentence HTML instead of using full paragraph
                        html_sentence = f"<p>{plain_sentence}</p>"
                        
                        # Create sentence object
                        class TestSentence:
                            def __init__(self, plain_text, html_text):
                                self.text = plain_text
                                self.html_text = html_text
                                self.start_char = 0
                                self.end_char = len(plain_text)
                        
                        sentences.append(TestSentence(plain_sentence, html_sentence))
            
            print(f"\n📝 Processed {len(sentences)} sentences:")
            for i, sent in enumerate(sentences, 1):
                print(f"\n  Sentence {i}:")
                print(f"    Plain: '{sent.text}'")
                print(f"    HTML:  '{sent.html_text}'")
                print(f"    Length: {len(sent.text)} chars, {len(sent.text.split())} words")
                
                # Check if this fixes the issue
                if sent.html_text != html_content:
                    print(f"    ✅ FIXED: HTML is now sentence-specific, not full paragraph!")
                else:
                    print(f"    ❌ PROBLEM: Still using full paragraph HTML")
        
        else:
            print("❌ spaCy not available")
    
    if __name__ == "__main__":
        test_sentence_processing()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This test requires the app modules to be available")
