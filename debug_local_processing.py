#!/usr/bin/env python3
"""
Local test of the sentence processing logic to debug the splitting issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import markdown
from bs4 import BeautifulSoup
import re

def get_spacy_model():
    """Import and return spaCy model for sentence segmentation"""
    try:
        import spacy
        # Try to load the English model
        try:
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except OSError:
            print("Warning: en_core_web_sm model not found, trying en_core_web_md")
            try:
                nlp = spacy.load("en_core_web_md")
                return nlp
            except OSError:
                print("Warning: No spaCy models found, sentence splitting will use simple regex")
                return None
    except ImportError:
        print("Warning: spaCy not available, sentence splitting will use simple regex")
        return None

def debug_sentence_processing():
    """Debug the sentence processing step by step."""
    
    print("🔍 LOCAL DEBUGGING OF SENTENCE PROCESSING")
    print("=" * 60)
    
    # Test with the problematic content
    test_markdown = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option."""
    
    print("Original markdown:")
    print(f'"{test_markdown}"')
    print()
    
    # Step 1: Convert markdown to HTML
    html_content = markdown.markdown(test_markdown)
    print("Step 1 - HTML after markdown conversion:")
    print(f'"{html_content}"')
    print()
    
    # Step 2: Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    print("Step 2 - BeautifulSoup parsing:")
    print(f"Soup: {soup}")
    print()
    
    # Step 3: Extract plain text (current method)
    plain_text = soup.get_text(separator=" ")
    print("Step 3 - Plain text extraction (current method):")
    print(f'"{plain_text}"')
    print()
    
    # Step 4: Find paragraph elements
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'li', 'blockquote'])
    print("Step 4 - Found HTML elements:")
    
    paragraph_blocks = []
    
    for i, element in enumerate(text_elements):
        print(f"  Element {i+1}: {element.name}")
        print(f"    Content: {element}")
        
        # Apply the fixed text extraction
        block_text = element.get_text(separator=" ").strip()
        print(f"    Extracted text: '{block_text}'")
        
        if len(block_text.strip()) > 2 and not re.match(r'^[.!?,:;\s]*$', block_text):
            paragraph_blocks.append({
                'plain': block_text,
                'html': str(element)
            })
            print(f"    ✅ Added to paragraph blocks")
        else:
            print(f"    ❌ Skipped (too short or punctuation only)")
        print()
    
    print(f"Step 5 - Paragraph blocks ({len(paragraph_blocks)} total):")
    for i, block in enumerate(paragraph_blocks):
        print(f"  Block {i+1}:")
        print(f"    Plain: '{block['plain']}'")
        print(f"    HTML: '{block['html']}'")
        print()
    
    # Step 6: spaCy processing
    spacy_nlp = get_spacy_model()
    print(f"Step 6 - spaCy processing (model available: {spacy_nlp is not None}):")
    
    if spacy_nlp:
        for i, block_data in enumerate(paragraph_blocks):
            plain_block = block_data['plain']
            print(f"  Processing block {i+1}: '{plain_block}'")
            
            doc = spacy_nlp(plain_block)
            sentence_list = list(doc.sents)
            
            print(f"    spaCy found {len(sentence_list)} sentences:")
            for j, sent in enumerate(sentence_list):
                print(f"      Sentence {j+1}: '{sent.text.strip()}'")
            print()
    else:
        print("    spaCy not available, would use regex fallback")
    
    print("🎯 DIAGNOSIS:")
    if len(paragraph_blocks) == 1:
        print("✅ Paragraph extraction is correct (1 block)")
        if spacy_nlp:
            doc = spacy_nlp(paragraph_blocks[0]['plain'])
            sents = list(doc.sents)
            if len(sents) == 1:
                print("✅ spaCy sentence splitting is correct (1 sentence)")
                print("🎉 The issue should be fixed!")
            else:
                print(f"❌ spaCy is incorrectly splitting into {len(sents)} sentences")
                print("🔧 Need to investigate spaCy sentence boundaries")
        else:
            print("⚠️ Cannot test spaCy - model not available")
    else:
        print(f"❌ Paragraph extraction is wrong ({len(paragraph_blocks)} blocks)")
        print("🔧 Need to fix HTML parsing logic")

if __name__ == "__main__":
    debug_sentence_processing()
