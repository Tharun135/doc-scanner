#!/usr/bin/env python3
"""
Test the improved sentence splitting that handles inline formatting.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import extract_sentences_from_html, split_text_into_sentences

def test_sentence_splitting():
    """Test sentence splitting with various formatting scenarios."""
    
    print("🔧 TESTING IMPROVED SENTENCE SPLITTING")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Bold text in middle of sentence",
            "html": "<p>This is a sentence with <strong>bold text</strong> in the middle.</p>",
            "expected": ["This is a sentence with bold text in the middle."]
        },
        {
            "name": "Link in middle of sentence", 
            "html": "<p>Click <a href='#'>this link</a> to continue reading.</p>",
            "expected": ["Click this link to continue reading."]
        },
        {
            "name": "Image in middle of sentence",
            "html": "<p>Here is an image <img src='test.jpg' alt='test'> in the sentence.</p>",
            "expected": ["Here is an image in the sentence."]
        },
        {
            "name": "Multiple formatting elements",
            "html": "<p>This <strong>bold</strong> and <em>italic</em> text with a <a href='#'>link</a> should stay together.</p>",
            "expected": ["This bold and italic text with a link should stay together."]
        },
        {
            "name": "Multiple sentences with formatting",
            "html": "<p>First sentence has <strong>bold</strong> text. Second sentence has <em>italic</em> text.</p>",
            "expected": ["First sentence has bold text.", "Second sentence has italic text."]
        },
        {
            "name": "Sentence spanning multiple elements",
            "html": "<p>This sentence starts here <strong>continues in bold</strong> and <em>ends in italic.</em></p>",
            "expected": ["This sentence starts here continues in bold and ends in italic."]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Input HTML: {test_case['html']}")
        
        # Test our extraction function
        result = extract_sentences_from_html(test_case['html'])
        
        print(f"Expected: {test_case['expected']}")
        print(f"Got:      {result}")
        
        if result == test_case['expected']:
            print("✅ PASS")
        else:
            print("❌ FAIL")
    
    print("\n" + "=" * 60)
    print("Testing plain text splitting:")
    
    text_tests = [
        {
            "text": "This is sentence one. This is sentence two.",
            "expected": ["This is sentence one.", "This is sentence two."]
        },
        {
            "text": "Question one? Statement two. Exclamation three!",
            "expected": ["Question one?", "Statement two.", "Exclamation three!"]
        }
    ]
    
    for i, test_case in enumerate(text_tests, 1):
        print(f"\n{i}. Plain text test")
        print(f"Input: {test_case['text']}")
        
        result = split_text_into_sentences(test_case['text'])
        
        print(f"Expected: {test_case['expected']}")
        print(f"Got:      {result}")
        
        if result == test_case['expected']:
            print("✅ PASS")
        else:
            print("❌ FAIL")

if __name__ == "__main__":
    test_sentence_splitting()
