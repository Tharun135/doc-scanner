#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup
import spacy
import re

# Test edge cases for sentence splitting
def test_edge_cases():
    # Read the test file
    with open('d:/doc-scanner/test_edge_cases.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print("=== MARKDOWN CONTENT ===")
    print(md_content)
    print("\n" + "="*60)
    
    # Convert to HTML
    html_content = markdown.markdown(md_content)
    print("=== HTML CONTENT ===")
    print(html_content)
    print("\n" + "="*60)
    
    # Use improved text extraction
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text = soup.get_text(separator=" ")
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== IMPROVED PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Process paragraph blocks
    paragraph_blocks = []
    for p_tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
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
        
        for block in paragraph_blocks:
            doc = nlp(block)
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3:
                    sentences.append(cleaned_text)
        
        print("=== FINAL SENTENCES (EDGE CASES) ===")
        for i, sent in enumerate(sentences):
            print(f"{i+1}: '{sent}'")
        print("\n" + "="*60)
        
        # Check for common issues
        issues = []
        for i, sent in enumerate(sentences):
            if re.search(r'\*\*[^*]+\*\*', sent):
                issues.append(f"Sentence {i+1} contains bold markdown (should be cleaned)")
            if re.search(r'`[^`]+`', sent):
                issues.append(f"Sentence {i+1} contains code markdown (should be cleaned)")
            if len(sent.split()) > 25:
                issues.append(f"Sentence {i+1} is very long ({len(sent.split())} words)")
        
        if issues:
            print("=== POTENTIAL ISSUES FOUND ===")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("=== NO FORMATTING ISSUES FOUND ===")
            print("All sentences appear to be properly cleaned!")
            
    except Exception as e:
        print(f"SpaCy error: {e}")

if __name__ == "__main__":
    test_edge_cases()
