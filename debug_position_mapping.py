#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

from app.app import parse_file_content
import markdown
from bs4 import BeautifulSoup
import spacy
import re
from app.app import get_spacy_model

def debug_position_mapping():
    """Debug the specific issue with position mapping for bold text."""
    
    # Test the specific case
    test_content = """# Test Case for Specific Issue

You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

This is another sentence with **bold text** to test the position mapping.

A sentence without formatting to compare."""
    
    print("=== ORIGINAL MARKDOWN ===")
    print(test_content)
    print("\n" + "="*60)
    
    # Process through the parsing pipeline
    html_content = markdown.markdown(test_content)
    print("=== HTML CONTENT ===")
    print(html_content)
    print("\n" + "="*60)
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Current approach - extract plain text  
    plain_text = soup.get_text(separator=" ")
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== CLEANED PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Extract paragraph blocks
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
    
    # Process sentences with spaCy
    spacy_nlp = get_spacy_model()
    sentences = []
    
    if spacy_nlp:
        for block in paragraph_blocks:
            doc = spacy_nlp(block)
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3 and not re.match(r'^[.!?,:;\s\-_]*$', cleaned_text):
                    sentences.append(sent)
    
    print("=== SENTENCES WITH SPACY POSITIONS ===")
    for i, sent in enumerate(sentences):
        print(f"{i+1}: '{sent.text}' (spaCy pos: {sent.start_char}-{sent.end_char})")
    print("\n" + "="*60)
    
    # Now test position mapping in plain text
    print("=== POSITION MAPPING TEST ===")
    for i, sent in enumerate(sentences):
        sentence_text = sent.text.strip()
        
        # Find position in plain text
        pos_in_plain = plain_text.find(sentence_text)
        print(f"Sentence {i+1}: '{sentence_text}'")
        print(f"  Found at position {pos_in_plain} in plain text")
        
        if pos_in_plain != -1:
            end_pos = pos_in_plain + len(sentence_text)
            print(f"  Range: {pos_in_plain}-{end_pos}")
            print(f"  Text slice: '{plain_text[pos_in_plain:end_pos]}'")
            
            # Check if this sentence ends properly
            if end_pos < len(plain_text):
                next_char = plain_text[end_pos]
                print(f"  Next character: '{next_char}' (ord: {ord(next_char)})")
                
                # The issue might be here - if the sentence doesn't include punctuation
                if sentence_text[-1] not in '.!?':
                    print(f"  ❌ PROBLEM: Sentence doesn't end with punctuation!")
                    print(f"  Looking for punctuation after position {end_pos}")
                    
                    # Look ahead for punctuation
                    for j in range(end_pos, min(end_pos + 10, len(plain_text))):
                        if plain_text[j] in '.!?':
                            print(f"  Found punctuation '{plain_text[j]}' at position {j}")
                            full_sentence = plain_text[pos_in_plain:j+1]
                            print(f"  CORRECTED SENTENCE: '{full_sentence}'")
                            break
                else:
                    print(f"  ✅ Sentence ends with punctuation")
        else:
            print(f"  ❌ PROBLEM: Sentence not found in plain text!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_position_mapping()
