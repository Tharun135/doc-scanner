#!/usr/bin/env python3
"""
Test script to verify markdown syntax handling
"""

import sys
import os
sys.path.append('.')

from app.rules.grammar_rules import check as check_grammar
from app.rules.style_rules import check as check_style

def test_markdown_syntax():
    print("🧪 Testing Markdown Info Syntax Handling")
    print("=" * 50)
    
    # Test 1: Markdown info syntax (should NOT be flagged)
    test_markdown = '<p>info "NOTICE"</p><p>warning "IMPORTANT"</p><p>note "REMEMBER"</p>'
    
    print("\n1. Testing markdown syntax (should be ignored):")
    print("Text:", test_markdown)
    
    grammar_result = check_grammar(test_markdown)
    print(f"Grammar issues: {len(grammar_result)}")
    for suggestion in grammar_result:
        print("  -", suggestion)
    
    style_result = check_style(test_markdown)
    print(f"Style issues: {len(style_result)}")
    for suggestion in style_result:
        print("  -", suggestion)
    
    # Test 2: Regular lowercase sentence (should be flagged)
    test_regular = '<p>this sentence should be flagged for starting lowercase.</p>'
    
    print("\n2. Testing regular lowercase (should be flagged):")
    print("Text:", test_regular)
    
    grammar_result2 = check_grammar(test_regular)
    print(f"Grammar issues: {len(grammar_result2)}")
    for suggestion in grammar_result2:
        print("  -", suggestion)
    
    # Test 3: Regular ALL CAPS (should be flagged)
    test_caps = '<p>This is REALLY IMPORTANT text.</p>'
    
    print("\n3. Testing regular ALL CAPS (should be flagged):")
    print("Text:", test_caps)
    
    style_result3 = check_style(test_caps)
    print(f"Style issues: {len(style_result3)}")
    for suggestion in style_result3:
        print("  -", suggestion)
    
    print("\n" + "=" * 50)
    print("🎉 Markdown Syntax Test Complete!")

if __name__ == "__main__":
    test_markdown_syntax()
