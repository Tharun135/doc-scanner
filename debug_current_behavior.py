#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup
import spacy
import re

def test_current_behavior():
    """Test how the current system handles bold, images, and links."""
    
    # Read the test file
    with open('d:/doc-scanner/test_all_issues.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print("=== ORIGINAL MARKDOWN ===")
    print(md_content)
    print("\n" + "="*60)
    
    # Convert to HTML (like the app does)
    html_content = markdown.markdown(md_content)
    print("=== HTML AFTER MARKDOWN CONVERSION ===")
    print(html_content)
    print("\n" + "="*60)
    
    # Test current approach from app.py
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Current approach (what I previously implemented)
    plain_text = soup.get_text(separator=" ")
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== CURRENT PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Process paragraph blocks
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
    
    # Test spaCy sentence splitting
    try:
        nlp = spacy.load("en_core_web_sm")
        sentences = []
        
        print("=== SPACY PROCESSING PER BLOCK ===")
        for block_idx, block in enumerate(paragraph_blocks):
            print(f"\nBlock {block_idx+1}: '{block}'")
            doc = nlp(block)
            block_sentences = []
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3:
                    sentences.append(cleaned_text)
                    block_sentences.append(cleaned_text)
                    print(f"  Sentence: '{cleaned_text}'")
            if not block_sentences:
                print("  No valid sentences found!")
        
        print(f"\n=== ALL FINAL SENTENCES (Total: {len(sentences)}) ===")
        for i, sent in enumerate(sentences):
            print(f"{i+1}: '{sent}'")
            
    except Exception as e:
        print(f"SpaCy error: {e}")
    
    # Also test what happens if we use the original problematic approach
    print(f"\n=== TESTING ORIGINAL PROBLEMATIC APPROACH ===")
    soup_orig = BeautifulSoup(html_content, "html.parser")
    plain_text_orig = soup_orig.get_text(separator="\n")  # Original approach
    
    print("Original approach plain text:")
    print(repr(plain_text_orig))
    
    lines_orig = [line.strip() for line in plain_text_orig.split('\n') if line.strip()]
    print(f"\nOriginal approach lines ({len(lines_orig)}):")
    for i, line in enumerate(lines_orig):
        print(f"{i+1}: '{line}'")

if __name__ == "__main__":
    test_current_behavior()
