#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

# Test the full pipeline to see if we can reproduce the issue
from app.app import parse_file_content, get_rules, review_document
from werkzeug.datastructures import FileStorage
from io import BytesIO
import json

def test_full_pipeline():
    """Test the complete upload and analysis pipeline."""
    
    # The exact content that caused the issue
    test_content = """# Project Settings

You can choose to set any project to Autostart mode by activating the **Enable Autostart** option.

This is another test sentence with **bold formatting** to verify the fix.

A normal sentence without any special formatting.
"""
    
    print("=== TESTING FULL PIPELINE ===")
    print("Test content:")
    print(test_content)
    print("\n" + "="*60)
    
    # Simulate the file upload process
    file_content = test_content.encode('utf-8')
    
    # Parse the content like the app does
    parsed_html = parse_file_content(file_content, "test.md")
    print("=== PARSED HTML ===")
    print(parsed_html)
    print("\n" + "="*60)
    
    # Now extract text and process sentences like the app does
    from bs4 import BeautifulSoup
    import re
    from app.app import get_spacy_model
    
    soup = BeautifulSoup(parsed_html, "html.parser")
    
    # Use the enhanced text extraction
    plain_text = soup.get_text(separator=" ")
    plain_text = re.sub(r'\s+', ' ', plain_text)
    plain_text = re.sub(r'\s+([.!?])', r'\1', plain_text)
    plain_text = re.sub(r'([.!?])([A-Z])', r'\1 \2', plain_text)
    plain_text = plain_text.strip()
    
    print("=== EXTRACTED PLAIN TEXT ===")
    print(repr(plain_text))
    print("\n" + "="*60)
    
    # Get rules and analyze document
    rules = get_rules()
    print(f"=== ANALYZING WITH {len(rules)} RULES ===")
    
    document_analysis = review_document(plain_text, rules)
    document_issues = document_analysis.get('issues', [])
    
    print(f"Found {len(document_issues)} issues:")
    for i, issue in enumerate(document_issues):
        print(f"  {i+1}. Issue at {issue.get('start', 'N/A')}-{issue.get('end', 'N/A')}")
        print(f"     Text: '{issue.get('text', 'N/A')}'")
        print(f"     Message: '{issue.get('message', 'N/A')}'")
    print("\n" + "="*60)
    
    # Extract paragraph blocks like the app does
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
    spacy_nlp = get_spacy_model()
    sentences = []
    
    if spacy_nlp:
        for block in paragraph_blocks:
            doc = spacy_nlp(block)
            for sent in doc.sents:
                cleaned_text = re.sub(r'\s+', ' ', sent.text.strip())
                if len(cleaned_text) > 3 and not re.match(r'^[.!?,:;\s\-_]*$', cleaned_text):
                    sentences.append(sent)
    
    print(f"=== EXTRACTED SENTENCES ({len(sentences)}) ===")
    for i, sent in enumerate(sentences):
        print(f"{i+1}: '{sent.text}'")
    print("\n" + "="*60)
    
    # Now test the position mapping like the app does
    sentence_position_map = []
    current_pos = 0
    
    for index, sent in enumerate(sentences):
        sentence_text = sent.text.strip()
        sentence_start = plain_text.find(sentence_text, current_pos)
        
        if sentence_start != -1:
            sentence_end = sentence_start + len(sentence_text)
            sentence_position_map.append({
                'index': index,
                'start': sentence_start,
                'end': sentence_end,
                'sentence': sent,
                'text': sentence_text
            })
            current_pos = sentence_end
            print(f"✅ Sentence {index}: mapped to {sentence_start}-{sentence_end}")
        else:
            print(f"❌ Sentence {index}: could not find position")
    
    print("\n" + "="*60)
    
    # Test issue assignment
    def find_sentence_for_issue(issue_start, issue_end):
        for sent_info in sentence_position_map:
            if (issue_start >= sent_info['start'] and issue_start < sent_info['end']) or \
               (issue_end > sent_info['start'] and issue_end <= sent_info['end']) or \
               (issue_start <= sent_info['start'] and issue_end >= sent_info['end']):
                return sent_info['index']
        return None
    
    print("=== ISSUE TO SENTENCE MAPPING ===")
    for i, issue in enumerate(document_issues):
        issue_start = issue.get('start', 0)
        issue_end = issue.get('end', 0)
        sentence_index = find_sentence_for_issue(issue_start, issue_end)
        
        print(f"Issue {i+1}: position {issue_start}-{issue_end}")
        print(f"  Text: '{issue.get('text', 'N/A')}'")
        print(f"  Message: '{issue.get('message', 'N/A')}'")
        
        if sentence_index is not None:
            sentence_info = sentence_position_map[sentence_index]
            print(f"  → Mapped to sentence {sentence_index}: '{sentence_info['text']}'")
            
            # Check if the issue text appears to be truncated
            issue_text = issue.get('text', '')
            sentence_text = sentence_info['text']
            
            if issue_text and issue_text in sentence_text:
                # Find where the issue text ends in the sentence
                issue_end_in_sentence = sentence_text.find(issue_text) + len(issue_text)
                remaining_text = sentence_text[issue_end_in_sentence:]
                print(f"  Issue text: '{issue_text}'")
                print(f"  Remaining in sentence: '{remaining_text}'")
                
                if remaining_text.strip() and not issue_text.endswith('.'):
                    print(f"  🚨 POTENTIAL PROBLEM: Issue text seems truncated!")
                    print(f"     Issue should probably include: '{remaining_text.strip()}'")
            
        else:
            print(f"  ❌ Could not map to any sentence")
        print()

if __name__ == "__main__":
    test_full_pipeline()
