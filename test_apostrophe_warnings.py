#!/usr/bin/env python3
"""
Test cases that should trigger apostrophe warnings
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.special_characters import check

test_cases = [
    "Tharun's laptop is working.",           # Possessive - should be OK
    "Download all the PDF's now.",           # Likely plural misuse
    "The API's are not responding.",         # Likely plural misuse  
    "We have many CPU's available.",         # Likely plural misuse
    "John's and Mary's books are here.",     # Both possessive - should be OK
    "The file's contents are corrupted.",    # Possessive - should be OK
]

for test_case in test_cases:
    print(f"\nTesting: {test_case}")
    result = check(test_case)
    apostrophe_warnings = [r for r in result if "apostrophe" in r.lower()]
    
    if apostrophe_warnings:
        print(f"  ⚠️  Warnings: {len(apostrophe_warnings)}")
        for warning in apostrophe_warnings:
            print(f"    - {warning}")
    else:
        print(f"  ✅ No apostrophe warnings")
