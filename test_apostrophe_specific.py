#!/usr/bin/env python3
"""
Test cases specifically designed to trigger plural misuse warnings
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.special_characters import check

# Test cases that should definitely trigger warnings (clear plural misuse)
plural_misuse_cases = [
    "The API's are down.",                    # Subject + verb = plural
    "All CPU's are working fine.",            # "All" + plural indicator
    "Download these PDF's immediately.",      # "These" + plural indicator  
    "Many server's are offline.",             # "Many" + plural indicator
    "Several application's crashed.",         # "Several" + plural indicator
]

# Test cases that should NOT trigger warnings (valid possessive)
possessive_cases = [
    "Tharun's laptop is working.",           # Clear possessive
    "The server's CPU is overheating.",      # Clear possessive
    "John's favorite book is here.",         # Clear possessive
    "The application's settings changed.",   # Clear possessive
]

print("Testing PLURAL MISUSE cases (should trigger warnings):")
print("=" * 60)

for test_case in plural_misuse_cases:
    print(f"\nTesting: {test_case}")
    result = check(test_case)
    apostrophe_warnings = [r for r in result if "apostrophe" in r.lower()]
    
    if apostrophe_warnings:
        print(f"  ✅ CORRECTLY flagged as plural misuse")
        for warning in apostrophe_warnings:
            print(f"    - {warning}")
    else:
        print(f"  ❌ MISSED - should have been flagged as plural misuse")

print("\n" + "=" * 60)
print("Testing POSSESSIVE cases (should NOT trigger warnings):")
print("=" * 60)

for test_case in possessive_cases:
    print(f"\nTesting: {test_case}")
    result = check(test_case)
    apostrophe_warnings = [r for r in result if "apostrophe" in r.lower()]
    
    if apostrophe_warnings:
        print(f"  ❌ INCORRECTLY flagged - this is valid possessive")
        for warning in apostrophe_warnings:
            print(f"    - {warning}")
    else:
        print(f"  ✅ CORRECTLY recognized as valid possessive")
