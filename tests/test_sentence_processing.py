#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import markdown
from bs4 import BeautifulSoup
from app.rules.concise_simple_words import check

# Simulate what happens when a markdown file is processed
def test_sentence_highlighting():
    # Read the test markdown file
    with open('d:/doc-scanner/test_media.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print("MARKDOWN CONTENT:")
    print(md_content)
    print("\n" + "="*60)
    
    # Convert to HTML (like the app does)
    html_content = markdown.markdown(md_content)
    print("HTML CONTENT:")
    print(html_content)
    print("\n" + "="*60)
    
    # Extract plain text (like the app does)
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text = soup.get_text(separator="\n")
    print("PLAIN TEXT:")
    print(plain_text)
    print("\n" + "="*60)
    
    # Split into sentences (simplified version)
    lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
    sentences = []
    for line in lines:
        import re
        simple_sentences = re.split(r'[.!?]+\s+', line)
        for sent_text in simple_sentences:
            if sent_text.strip():
                sentences.append(sent_text.strip())
    
    print("SENTENCES:")
    for i, sentence in enumerate(sentences):
        print(f"{i}: {sentence}")
    print("\n" + "="*60)
    
    # Check each sentence for issues
    print("RULE ANALYSIS:")
    for i, sentence in enumerate(sentences):
        suggestions = check(sentence)
        if suggestions:
            print(f"Sentence {i}: {sentence}")
            for suggestion in suggestions:
                print(f"  → {suggestion}")
            print()

if __name__ == "__main__":
    test_sentence_highlighting()
