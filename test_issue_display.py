#!/usr/bin/env python3
"""
Test to verify that issue messages no longer include the original sentence.
"""

import sys
import os
sys.path.append('app')

from rules import long_sentences, can_may_terms, concise_simple_words

def test_long_sentence_display():
    """Test that long sentence issues don't include the sentence."""
    print("🧪 Testing Long Sentence Issue Display")
    print("=" * 50)
    
    test_content = "This is a very long sentence that contains more than twenty-five words which should trigger the long sentence detection rule and show only the issue description without including the original sentence text in the display."
    
    suggestions = long_sentences.check(test_content)
    
    if suggestions:
        print(f"✅ Suggestion found: {suggestions[0]}")
        
        # Check if it contains "Original sentence:"
        if "Original sentence:" in suggestions[0]:
            print("❌ FAIL: Issue still contains original sentence")
        else:
            print("✅ PASS: Issue only contains description")
    else:
        print("❌ No suggestions found")
    print()

def test_modal_verb_display():
    """Test that modal verb issues don't include the sentence."""
    print("🧪 Testing Modal Verb Issue Display")
    print("=" * 50)
    
    test_content = "You can access the system through the web interface."
    
    suggestions = can_may_terms.check(test_content)
    
    if suggestions:
        for i, suggestion in enumerate(suggestions):
            print(f"✅ Suggestion {i+1}: {suggestion}")
            
            # Check if it contains "Original sentence:"
            if "Original sentence:" in suggestion:
                print("❌ FAIL: Issue still contains original sentence")
            else:
                print("✅ PASS: Issue only contains description")
    else:
        print("❌ No suggestions found")
    print()

def test_concise_words_display():
    """Test that concise words issues don't include the sentence."""
    print("🧪 Testing Concise Words Issue Display")
    print("=" * 50)
    
    test_content = "It is important to utilize the best practices very carefully."
    
    suggestions = concise_simple_words.check(test_content)
    
    if suggestions:
        for i, suggestion in enumerate(suggestions):
            print(f"✅ Suggestion {i+1}: {suggestion}")
            
            # Check if it contains "Original sentence:"
            if "Original sentence:" in suggestion:
                print("❌ FAIL: Issue still contains original sentence")
            else:
                print("✅ PASS: Issue only contains description")
    else:
        print("❌ No suggestions found")
    print()

if __name__ == "__main__":
    print("Testing Issue Display - Should Only Show Issues, Not Sentences")
    print("=" * 70)
    print()
    
    test_long_sentence_display()
    test_modal_verb_display()
    test_concise_words_display()
    
    print("=" * 70)
    print("Testing complete!")
