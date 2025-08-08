#!/usr/bin/env python3

"""
Final comprehensive test of all file extension exclusions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rules.technical_terms import check

def test_all_file_extensions():
    """Test all file format capitalization rules with extensions."""
    
    test_cases = [
        # File extensions - should NOT be flagged
        {"text": "Save as .json file.", "should_flag": False, "format": "JSON"},
        {"text": "Edit the .xml config.", "should_flag": False, "format": "XML"},
        {"text": "Open .html page.", "should_flag": False, "format": "HTML"},
        {"text": "Load .css styles.", "should_flag": False, "format": "CSS"},
        
        # General format references - SHOULD be flagged
        {"text": "Use json format.", "should_flag": True, "format": "JSON"},
        {"text": "Parse xml data.", "should_flag": True, "format": "XML"},
        {"text": "Write html markup.", "should_flag": True, "format": "HTML"},
        {"text": "Apply css rules.", "should_flag": True, "format": "CSS"},
        
        # Complex cases
        {"text": "The .json file contains json data.", "should_flag": True, "format": "JSON"},
        {"text": "Edit .css and update css styling.", "should_flag": True, "format": "CSS"},
        {"text": "Save .html with proper html structure.", "should_flag": True, "format": "HTML"},
        {"text": "Parse .xml using xml parser.", "should_flag": True, "format": "XML"},
        
        # Already correct - should NOT be flagged
        {"text": "Use JSON format.", "should_flag": False, "format": "JSON"},
        {"text": "Parse XML data.", "should_flag": False, "format": "XML"},
        {"text": "Write HTML markup.", "should_flag": False, "format": "HTML"},
        {"text": "Apply CSS rules.", "should_flag": False, "format": "CSS"},
    ]
    
    print("🧪 FINAL COMPREHENSIVE TEST - ALL FILE EXTENSIONS")
    print("=" * 80)
    print("Testing JSON, XML, HTML, CSS capitalization with file extension exclusions")
    print("=" * 80)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 TEST {i}: {test_case['text']}")
        
        suggestions = check(test_case['text'])
        format_suggestions = [s for s in suggestions if test_case['format'] in s]
        
        has_flags = len(format_suggestions) > 0
        
        print(f"   Expected: {'Flag' if test_case['should_flag'] else 'No flag'}")
        print(f"   Actual: {'Flag' if has_flags else 'No flag'}")
        
        if test_case['should_flag'] == has_flags:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL")
            print(f"   Suggestions: {format_suggestions}")
            all_passed = False
    
    print(f"\n{'='*80}")
    if all_passed:
        print("🎉 ALL TESTS PASS: File extension exclusions working perfectly!")
        print("✅ File extensions (.json, .xml, .html, .css) are NOT flagged")
        print("✅ General format references (json, xml, html, css) ARE flagged")
        print("✅ Already correct formats (JSON, XML, HTML, CSS) are NOT flagged")
    else:
        print("❌ SOME TESTS FAILED: Rule needs more work!")
    
    return all_passed

if __name__ == "__main__":
    test_all_file_extensions()
