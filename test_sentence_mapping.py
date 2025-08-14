#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

from app.app import upload_file, parse_file_content
import markdown
from bs4 import BeautifulSoup
import spacy
import re

# Test that sentence mapping works correctly for the fixed parsing
def test_sentence_issue_mapping():
    # Create test markdown content with various formatting
    test_content = """# Test Document

This is a **normal sentence** without issues.

This sentence has some issues because it is very very very long and contains passive voice that should be detected by the system.

Here is another sentence with **bold formatting** and some inline `code snippets` that should stay together.

The image reference 176617096203-d2e2393 appears in this sentence and should not cause splitting.

A sentence with **multiple** formatting and `code` and image 987654321-test should work correctly.
"""

    print("=== TEST CONTENT ===")
    print(test_content)
    print("\n" + "="*60)
    
    # Process through the app's parsing pipeline
    html_content = markdown.markdown(test_content)
    print("=== HTML CONTENT ===")
    print(html_content)
    print("\n" + "="*60)
    
    # Use the improved parsing method from the app
    soup = BeautifulSoup(html_content, "html.parser")
    
    # FIXED: Improved text extraction to preserve sentence integrity
    plain_text = soup.get_text(separator=" ")
    
    # Clean up excessive whitespace and normalize text
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== CLEANED PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Process paragraph blocks for sentence segmentation
    paragraph_blocks = []
    for p_tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        block_text = p_tag.get_text(separator=" ").strip()
        if block_text:
            block_text = re.sub(r'\s+', ' ', block_text)
            paragraph_blocks.append(block_text)
    
    print("=== PARAGRAPH BLOCKS ===")
    for i, block in enumerate(paragraph_blocks):
        print(f"{i+1}: '{block}'")
    print("\n" + "="*60)
    
    # Extract sentences using spaCy
    try:
        nlp = spacy.load("en_core_web_sm")
        sentences = []
        
        for block in paragraph_blocks:
            doc = nlp(block)
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3:
                    sentences.append(sent)
        
        print("=== FINAL SENTENCES ===")
        for i, sent in enumerate(sentences):
            print(f"{i+1}: '{sent.text}'")
            print(f"    Characters: {sent.start_char}-{sent.end_char}")
        print("\n" + "="*60)
        
        # Test position mapping
        sentence_position_map = []
        current_pos = 0
        for index, sent in enumerate(sentences):
            sentence_start = plain_text.find(sent.text, current_pos)
            if sentence_start != -1:
                sentence_end = sentence_start + len(sent.text)
                sentence_position_map.append({
                    'index': index,
                    'start': sentence_start,
                    'end': sentence_end,
                    'sentence': sent
                })
                current_pos = sentence_end
            else:
                print(f"WARNING: Could not find sentence {index} in plain text")
        
        print("=== SENTENCE POSITION MAPPING ===")
        for mapping in sentence_position_map:
            print(f"Sentence {mapping['index']}: pos {mapping['start']}-{mapping['end']}")
            print(f"  Text: '{mapping['sentence'].text}'")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"SpaCy error: {e}")

if __name__ == "__main__":
    test_sentence_issue_mapping()
