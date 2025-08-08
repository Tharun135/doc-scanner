#!/usr/bin/env python3

"""
Check if HTML/CSS also need file extension exclusions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.technical_terms import check

def test_html_css_extensions():
    """Test if HTML/CSS file extensions are incorrectly flagged."""
    
    test_cases = [
        {
            "text": "Save as .html file.",
            "format": "HTML",
            "should_flag": False
        },
        {
            "text": "Edit the .css stylesheet.",
            "format": "CSS", 
            "should_flag": False
        },
        {
            "text": "Use html for markup.",
            "format": "HTML",
            "should_flag": True
        },
        {
            "text": "Apply css styling.",
            "format": "CSS",
            "should_flag": True
        }
    ]
    
    print("🧪 CHECKING HTML/CSS FILE EXTENSIONS")
    print("=" * 50)
    
    needs_fix = False
    
    for test_case in test_cases:
        print(f"\n📝 Testing: \"{test_case['text']}\"")
        
        suggestions = check(test_case['text'])
        format_suggestions = [s for s in suggestions if test_case['format'] in s]
        
        has_flags = len(format_suggestions) > 0
        
        print(f"   Should flag: {test_case['should_flag']}")
        print(f"   Actually flagged: {has_flags}")
        print(f"   Suggestions: {format_suggestions}")
        
        if test_case['should_flag'] != has_flags:
            print("   ⚠️  NEEDS ATTENTION")
            if not test_case['should_flag'] and has_flags:
                needs_fix = True
        else:
            print("   ✅ OK")
    
    if needs_fix:
        print(f"\n⚠️  HTML/CSS file extensions also need fixing!")
        return True
    else:
        print(f"\n✅ HTML/CSS file extensions are OK")
        return False

if __name__ == "__main__":
    test_html_css_extensions()
