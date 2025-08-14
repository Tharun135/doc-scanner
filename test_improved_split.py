#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup
import spacy
import re

# Test the improved sentence splitting
def test_improved_sentence_splitting():
    # Read the test file
    with open('d:/doc-scanner/test_sentence_splitting_issue.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print("=== MARKDOWN CONTENT ===")
    print(md_content)
    print("\n" + "="*60)
    
    # Convert to HTML (like the app does)
    html_content = markdown.markdown(md_content)
    print("=== HTML CONTENT ===")
    print(html_content)
    print("\n" + "="*60)
    
    # NEW: Improved text extraction method
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Use space as separator to prevent breaking sentences with formatting
    plain_text = soup.get_text(separator=" ")
    
    # Clean up excessive whitespace and normalize text
    # Replace multiple spaces with single space
    plain_text = re.sub(r'\s+', ' ', plain_text)
    # Clean up spacing around punctuation
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    # Ensure proper spacing after punctuation
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== IMPROVED PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Process paragraph blocks
    paragraph_blocks = []
    for p_tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        block_text = p_tag.get_text(separator=" ").strip()
        if block_text:
            # Clean the block text 
            block_text = re.sub(r'\s+', ' ', block_text)
            paragraph_blocks.append(block_text)
    
    print("=== PARAGRAPH BLOCKS ===")
    for i, block in enumerate(paragraph_blocks):
        print(f"{i+1}: '{block}'")
    print("\n" + "="*60)
    
    # Test spaCy sentence splitting on clean blocks
    try:
        nlp = spacy.load("en_core_web_sm")
        sentences = []
        
        for block in paragraph_blocks:
            doc = nlp(block)
            for sent in doc.sents:
                # Clean up the sentence text and skip very short fragments
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3:  # Skip very short fragments
                    sentences.append(cleaned_text)
        
        print("=== IMPROVED SPACY SENTENCES ===")
        for i, sent in enumerate(sentences):
            print(f"{i+1}: '{sent}'")
        print("\n" + "="*60)
    except Exception as e:
        print(f"SpaCy not available: {e}")
    
    # Test improved regex fallback
    sentences_fallback = []
    for block in paragraph_blocks:
        # Split by sentence-ending punctuation followed by space and capital letter
        simple_sentences = re.split(r'[.!?]+\s+(?=[A-Z])', block)
        for sent_text in simple_sentences:
            if sent_text.strip() and len(sent_text.strip()) > 3:
                cleaned = re.sub(r'\s+', ' ', sent_text.strip())
                sentences_fallback.append(cleaned)
    
    print("=== IMPROVED REGEX FALLBACK SENTENCES ===")
    for i, sent in enumerate(sentences_fallback):
        print(f"{i+1}: '{sent}'")
    print("\n" + "="*60)

if __name__ == "__main__":
    test_improved_sentence_splitting()
