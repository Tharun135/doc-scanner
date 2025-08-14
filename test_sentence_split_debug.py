#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup
import spacy

# Test the sentence splitting issue
def test_sentence_splitting():
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
    
    # Extract plain text (like the app does)
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text = soup.get_text(separator="\n")
    print("=== PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Test spaCy sentence splitting
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(plain_text)
        
        print("=== SPACY SENTENCES ===")
        for i, sent in enumerate(doc.sents):
            print(f"{i+1}: '{sent.text}'")
            print(f"    Start: {sent.start_char}, End: {sent.end_char}")
        print("\n" + "="*60)
    except Exception as e:
        print(f"SpaCy not available: {e}")
    
    # Test fallback regex splitting (like the app does when spaCy fails)
    import re
    lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
    sentences = []
    for line in lines:
        simple_sentences = re.split(r'[.!?]+\s+', line)
        for sent_text in simple_sentences:
            if sent_text.strip():
                sentences.append(sent_text.strip())
    
    print("=== REGEX FALLBACK SENTENCES ===")
    for i, sent in enumerate(sentences):
        print(f"{i+1}: '{sent}'")
    print("\n" + "="*60)

if __name__ == "__main__":
    test_sentence_splitting()
