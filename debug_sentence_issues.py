#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.app import app
import tempfile
import os
import json
from app.app import parse_file
from bs4 import BeautifulSoup

def debug_sentence_processing():
    # Test content with the problematic patterns
    test_content = '''# Test Document

You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

This sentence has **bold words** in the middle of it.

Here is a sentence with a [link](https://example.com) embedded.
'''

    print("=== DEBUGGING SENTENCE PROCESSING ISSUES ===")
    print(f"Original content:\n{test_content}")
    print("\n" + "="*60)
    
    # Step 1: Parse file to HTML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Parse to HTML
        with open(temp_file, 'rb') as f:
            html_content = parse_file(type('MockFile', (), {'filename': 'test.md', 'read': f.read})())
        
        print(f"=== HTML CONTENT ===")
        print(html_content)
        print("\n" + "="*60)
        
        # Step 2: Extract text using our current method
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Current method - using space separator
        plain_text = soup.get_text(separator=" ")
        print(f"=== PLAIN TEXT (space separator) ===")
        print(f"'{plain_text}'")
        print("\n" + "="*60)
        
        # Let's also test other extraction methods
        plain_text_newline = soup.get_text(separator="\n")
        print(f"=== PLAIN TEXT (newline separator) ===")
        print(f"'{plain_text_newline}'")
        print("\n" + "="*60)
        
        plain_text_none = soup.get_text()
        print(f"=== PLAIN TEXT (no separator) ===")
        print(f"'{plain_text_none}'")
        print("\n" + "="*60)
        
        # Step 3: Test sentence splitting with spaCy
        from app.rules.spacy_utils import get_spacy_model
        spacy_nlp = get_spacy_model()
        
        if spacy_nlp:
            doc = spacy_nlp(plain_text)
            print(f"=== SPACY SENTENCE SPLITTING ===")
            for i, sent in enumerate(doc.sents):
                print(f"Sentence {i}: '{sent.text}' (start: {sent.start_char}, end: {sent.end_char})")
        else:
            print("=== SPACY NOT AVAILABLE ===")
        
        print("\n" + "="*60)
        
        # Step 4: Test the actual upload endpoint
        with app.test_client() as client:
            with open(temp_file, 'rb') as f:
                response = client.post('/upload', 
                                     data={'file': (f, 'test.md')},
                                     content_type='multipart/form-data')
            
            if response.status_code == 200:
                result = response.get_json()
                print(f"=== UPLOAD ENDPOINT RESULT ===")
                print(f"Status: SUCCESS")
                print(f"Number of sentences: {len(result.get('sentences', []))}")
                
                for i, sentence_data in enumerate(result.get('sentences', [])):
                    print(f"\nSentence {i}:")
                    print(f"  Text: '{sentence_data.get('sentence', '')}'")
                    print(f"  HTML Segment: '{sentence_data.get('html_segment', 'None')}'")
                    print(f"  Words: {sentence_data.get('words', [])}")
                    print(f"  Start: {sentence_data.get('start', 'N/A')}")
                    print(f"  End: {sentence_data.get('end', 'N/A')}")
                    print(f"  Feedback: {len(sentence_data.get('feedback', []))} issues")
                
                # Check for the "dex=" issue in HTML content
                content = result.get('content', '')
                if 'dex=' in content:
                    print(f"\n=== FOUND 'dex=' ISSUE ===")
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'dex=' in line:
                            print(f"Line {i}: {line}")
                            # Show context
                            start = max(0, i-2)
                            end = min(len(lines), i+3)
                            print("Context:")
                            for j in range(start, end):
                                marker = " >>> " if j == i else "     "
                                print(f"{marker}{j}: {lines[j]}")
            else:
                print(f"=== UPLOAD FAILED ===")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")
    
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    debug_sentence_processing()
