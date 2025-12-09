#!/usr/bin/env python3
"""
Test script to verify title exclusion functionality
"""

import sys
import os
sys.path.append('.')

from app.rules.long_sentence import check as check_long_sentence
from app.rules.grammar_rules import check as check_grammar
from app.rules.style_rules import check as check_style
from app.rules.readability_rules import check as check_readability

def test_title_exclusion():
    print("🧪 Testing Title Exclusion Functionality")
    print("=" * 60)
    
    # Test 1: HTML headings (should be excluded)
    test_html_headings = '''
    <h1>This is a Very Long Title That Would Normally Be Flagged for Being Too Long</h1>
    <h2>CONFIGURATION SETTINGS</h2>
    <h3>getting started guide</h3>
    <p>This is a regular sentence that should be checked normally for grammar and style issues.</p>
    '''
    
    print("\n1. Testing HTML headings (should be excluded):")
    print("Content:", test_html_headings.strip())
    
    results = {
        "Long Sentence": check_long_sentence(test_html_headings),
        "Grammar": check_grammar(test_html_headings), 
        "Style": check_style(test_html_headings),
        "Readability": check_readability(test_html_headings)
    }
    
    for rule_name, suggestions in results.items():
        print(f"\n  {rule_name}: {len(suggestions)} issues")
        for suggestion in suggestions:
            print(f"    - {suggestion[:80]}...")
    
    # Test 2: Markdown-style headings
    test_markdown = '''
    <p># Main Title With Many Words That Could Be Flagged</p>
    <p>## SECTION OVERVIEW</p>
    <p>### getting started</p>
    <p>this sentence should be flagged for lowercase.</p>
    '''
    
    print("\n\n2. Testing Markdown headings:")
    print("Content:", test_markdown.strip())
    
    results2 = {
        "Long Sentence": check_long_sentence(test_markdown),
        "Grammar": check_grammar(test_markdown),
        "Style": check_style(test_markdown)
    }
    
    for rule_name, suggestions in results2.items():
        print(f"\n  {rule_name}: {len(suggestions)} issues")
        for suggestion in suggestions:
            print(f"    - {suggestion[:80]}...")
    
    # Test 3: Title-like content (short, capitalized, no punctuation)
    test_title_like = '''
    <p>Introduction</p>
    <p>Getting Started</p>
    <p>INSTALLATION GUIDE</p>
    <p>1. Configuration</p>
    <p>2.1 Basic Setup</p>
    <p>this regular sentence should still be checked.</p>
    '''
    
    print("\n\n3. Testing title-like content:")
    print("Content:", test_title_like.strip())
    
    results3 = {
        "Grammar": check_grammar(test_title_like),
        "Style": check_style(test_title_like)
    }
    
    for rule_name, suggestions in results3.items():
        print(f"\n  {rule_name}: {len(suggestions)} issues")
        for suggestion in suggestions:
            print(f"    - {suggestion[:80]}...")
    
    print("\n" + "=" * 60)
    print("🎉 Title Exclusion Test Complete!")
    print("\nExpected behavior:")
    print("✅ Headings and titles should NOT be flagged")
    print("✅ Regular sentences should still be checked")

if __name__ == "__main__":
    test_title_exclusion()
