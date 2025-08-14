#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

# Import the Flask app and test the upload function directly
from app.app import upload_file, parse_file_content
from werkzeug.datastructures import FileStorage
from io import BytesIO
import json

def test_upload_function_directly():
    """Test the upload function directly without going through HTTP."""
    
    test_content = """# Test Document for All Issues

This is a normal sentence without any formatting.

This sentence has a **bold word** in the middle and should stay together.

This sentence contains an image reference 176617096203-d2e2393 which should not split.

This sentence has a [link to example](https://example.com) which should also stay together.

This complex sentence has **bold text**, an image 987654321-test, and a [link](https://test.com) all together.

Another sentence with [multiple links](https://first.com) and [second link](https://second.com) should work.

Final sentence with **bold**, `code`, image 123456789-final, and [link](https://final.com) combined.
"""
    
    print("=== TESTING UPLOAD FUNCTION DIRECTLY ===")
    print("Test content:")
    print(test_content)
    print("\n" + "="*60)
    
    # Create a file-like object
    file_content = test_content.encode('utf-8')
    file_obj = BytesIO(file_content)
    
    # Create a FileStorage object (what Flask would normally create)
    file_storage = FileStorage(
        stream=file_obj,
        filename="test.md",
        content_type="text/markdown"
    )
    
    # Test the parse_file_content function first
    parsed_content = parse_file_content(file_content, "test.md")
    print("=== PARSED HTML CONTENT ===")
    print(parsed_content)
    print("\n" + "="*60)
    
    # Now test the full upload logic by extracting the key parts
    from bs4 import BeautifulSoup
    import re
    from app.app import get_spacy_model
    
    html_content = parsed_content
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Use the fixed approach
    plain_text = soup.get_text(separator=" ")
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== EXTRACTED PLAIN TEXT ===")
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
    
    # Process sentences
    sentences = []
    spacy_nlp = get_spacy_model()
    
    print("=== SENTENCE PROCESSING ===")
    print(f"SpaCy available: {spacy_nlp is not None}")
    
    for block_idx, block in enumerate(paragraph_blocks):
        print(f"\nProcessing block {block_idx+1}: '{block}'")
        
        if spacy_nlp:
            doc = spacy_nlp(block)
            block_sentences = []
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3:
                    sentences.append(sent)
                    block_sentences.append(cleaned_text)
                    print(f"  Sentence: '{cleaned_text}'")
            if not block_sentences:
                print("  No valid sentences found!")
        else:
            print("  Using fallback regex splitting")
            simple_sentences = re.split(r'[.!?]+\s+(?=[A-Z])', block)
            for sent_text in simple_sentences:
                if sent_text.strip() and len(sent_text.strip()) > 3:
                    class SimpleSentence:
                        def __init__(self, text):
                            self.text = re.sub(r'\s+', ' ', text.strip())
                            self.start_char = 0
                            self.end_char = len(self.text)
                    sentences.append(SimpleSentence(sent_text.strip()))
                    print(f"  Sentence: '{sent_text.strip()}'")
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total sentences found: {len(sentences)}")
    
    for i, sent in enumerate(sentences):
        print(f"{i+1}: '{sent.text}'")
    
    # Check for problematic splits
    problems = []
    for i, sent in enumerate(sentences):
        text = sent.text
        if (text.strip() in ['bold word', 'bold text', 'bold', 'code', 'link', 'multiple links', 'second link'] or
            text.strip().endswith('has a') or 
            text.strip().endswith('sentence with') or
            text.strip().endswith('Final sentence with')):
            problems.append(f"Sentence {i+1}: '{text}' - looks like incorrect split")
    
    if problems:
        print(f"\n❌ PROBLEMS DETECTED ({len(problems)}):")
        for problem in problems:
            print(f"  {problem}")
        print("\nThe issue is NOT fully fixed!")
    else:
        print(f"\n✅ NO SPLITTING PROBLEMS DETECTED")
        print("The fix appears to be working correctly!")

if __name__ == "__main__":
    test_upload_function_directly()
