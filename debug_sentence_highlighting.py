#!/usr/bin/env python3
"""Debug sentence highlighting issue"""

from app.app import get_rules, review_document
from bs4 import BeautifulSoup
import sys
sys.path.append('app')

def debug_sentence_indexing():
    """Debug how sentences are indexed and mapped"""
    
    # Test content with known issue
    test_content = """Enable autostart to start the application automatically.

You can choose to set any project to Autostart mode by activating the"""
    
    print("=" * 60)
    print("DEBUGGING SENTENCE INDEXING")
    print("=" * 60)
    print(f"Test content:\n{repr(test_content)}")
    print()
    
    # Process like the web interface does
    soup = BeautifulSoup(test_content, "html.parser")
    plain_text = soup.get_text(separator="\n")
    
    # Split into sentences like web interface
    lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
    sentences = []
    
    print("Lines found:")
    for i, line in enumerate(lines):
        print(f"  {i}: {repr(line)}")
    print()
    
    # Split sentences like the web interface
    for line in lines:
        import re
        simple_sentences = re.split(r'[.!?]+\s+', line)
        for sent_text in simple_sentences:
            if sent_text.strip():
                class SimpleSentence:
                    def __init__(self, text, start_pos=0):
                        self.text = text.strip()
                        self.start_char = start_pos
                        self.end_char = start_pos + len(text)
                sentences.append(SimpleSentence(sent_text.strip()))
    
    print("Sentences created:")
    for i, sent in enumerate(sentences):
        print(f"  Sentence {i}: {repr(sent.text)}")
    print()
    
    # Get document issues
    rules = get_rules()
    document_analysis = review_document(plain_text, rules)
    document_issues = document_analysis.get('issues', [])
    
    print("Document issues:")
    for i, issue in enumerate(document_issues):
        print(f"  Issue {i}: {issue.get('message', '')}")
        print(f"    Text: {repr(issue.get('text', ''))}")
        print(f"    Position: {issue.get('start', 0)}-{issue.get('end', 0)}")
        
        # Find the actual text at that position
        start = issue.get('start', 0)
        end = issue.get('end', 0)
        if start < len(plain_text) and end <= len(plain_text) and start < end:
            actual_text = plain_text[start:end]
            print(f"    Actual text at position: {repr(actual_text)}")
        print()
    
    # Build sentence position mapping
    sentence_position_map = []
    current_pos = 0
    
    for index, sent in enumerate(sentences):
        sentence_start = plain_text.find(sent.text, current_pos)
        if sentence_start != -1:
            sentence_end = sentence_start + len(sent.text)
            sentence_position_map.append({
                'index': index,
                'start': sentence_start,
                'end': sentence_end,
                'sentence': sent
            })
            current_pos = sentence_end
            print(f"Sentence {index} position mapping: {sentence_start}-{sentence_end} = {repr(sent.text)}")
    
    print()
    
    # Map issues to sentences
    def find_sentence_for_issue(issue_start, issue_end):
        for sent_info in sentence_position_map:
            if (issue_start >= sent_info['start'] and issue_start < sent_info['end']) or \
               (issue_end > sent_info['start'] and issue_end <= sent_info['end']) or \
               (issue_start <= sent_info['start'] and issue_end >= sent_info['end']):
                return sent_info['index']
        return None
    
    print("Issue to sentence mapping:")
    for i, issue in enumerate(document_issues):
        issue_start = issue.get('start', 0)
        issue_end = issue.get('end', 0)
        
        if issue_start > 0 or issue_end > 0:
            sentence_index = find_sentence_for_issue(issue_start, issue_end)
            if sentence_index is not None:
                print(f"  Issue {i} '{issue.get('message', '')}' -> Sentence {sentence_index}: {repr(sentences[sentence_index].text)}")
            else:
                print(f"  Issue {i} '{issue.get('message', '')}' -> NO SENTENCE MATCH")
        else:
            print(f"  Issue {i} '{issue.get('message', '')}' -> NO POSITION INFO")
    
    return sentences, document_issues, sentence_position_map

if __name__ == "__main__":
    debug_sentence_indexing()
