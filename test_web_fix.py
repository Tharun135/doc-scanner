#!/usr/bin/env python3
"""Test the web interface issue assignment fix"""

from app.app import get_rules, review_document
from bs4 import BeautifulSoup
import sys
sys.path.append('app')

def simulate_web_interface_processing(content):
    """Simulate how the web interface processes content"""
    
    # Parse content like the web interface does
    html_content = content  # Assume it's already text
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text = soup.get_text(separator="\n")
    
    print(f"Plain text: {repr(plain_text)}")
    print()
    
    # Split into sentences like the web interface does
    lines = [line.strip() for line in plain_text.split('\n') if line.strip()]
    sentences = []
    for line in lines:
        # Simple sentence splitting for this test
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
    
    print(f"Sentences found: {len(sentences)}")
    for i, sent in enumerate(sentences):
        print(f"  {i+1}. \"{sent.text}\"")
    print()
    
    # Analyze the full document
    rules = get_rules()
    document_analysis = review_document(plain_text, rules)
    document_issues = document_analysis.get('issues', [])
    
    print(f"Document issues found: {len(document_issues)}")
    for i, issue in enumerate(document_issues):
        print(f"  {i+1}. {issue.get('message', '')} (text: \"{issue.get('text', '')}\", pos: {issue.get('start', 0)}-{issue.get('end', 0)})")
    print()
    
    # Build position mapping like the fixed web interface
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
            print(f"Sentence {index+1} mapped to position {sentence_start}-{sentence_end}: \"{sent.text}\"")
    print()
    
    # Function to find which sentence contains an issue
    def find_sentence_for_issue(issue_start, issue_end):
        for sent_info in sentence_position_map:
            if (issue_start >= sent_info['start'] and issue_start < sent_info['end']) or \
               (issue_end > sent_info['start'] and issue_end <= sent_info['end']) or \
               (issue_start <= sent_info['start'] and issue_end >= sent_info['end']):
                return sent_info['index']
        return None
    
    # Map issues to sentences
    sentence_feedback_map = {i: [] for i in range(len(sentences))}
    unmatched_issues = []
    
    for issue in document_issues:
        issue_start = issue.get('start', 0)
        issue_end = issue.get('end', 0)
        
        if issue_start > 0 or issue_end > 0:
            sentence_index = find_sentence_for_issue(issue_start, issue_end)
            if sentence_index is not None:
                sentence_feedback_map[sentence_index].append(issue)
                print(f"✅ Issue \"{issue.get('message', '')}\" assigned to sentence {sentence_index+1}: \"{sentences[sentence_index].text}\"")
            else:
                unmatched_issues.append(issue)
                print(f"❌ Issue \"{issue.get('message', '')}\" could not be matched to any sentence")
        else:
            unmatched_issues.append(issue)
            print(f"⚠️ Issue \"{issue.get('message', '')}\" has no position info - this rule needs fixing")
    
    print()
    print("Final sentence assignments:")
    for i, sent in enumerate(sentences):
        issues = sentence_feedback_map[i]
        print(f"  Sentence {i+1}: \"{sent.text}\" -> {len(issues)} issues")
        for issue in issues:
            print(f"    - {issue.get('message', '')}")

# Test cases
print("=" * 60)
print("TEST 1: Enable autostart alone (should have no issues)")
print("=" * 60)
simulate_web_interface_processing("Enable autostart")

print("\n" + "=" * 60)
print("TEST 2: Document with 'choose from menu' (should be assigned correctly)")
print("=" * 60)
test_content = """
Enable autostart to start the application automatically.

You can choose different options from the menu. This allows better control.
"""
simulate_web_interface_processing(test_content)
