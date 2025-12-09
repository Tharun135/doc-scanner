#!/usr/bin/env python3
"""
Test the exact scenario the user is experiencing
"""

import sys
import os
sys.path.append('.')

# Simulate the user's exact scenario
user_content = """
<h2>Generating the connector configuration</h2>
<p>Some content here.</p>
"""

print("🔍 Testing user's exact scenario...")
print(f"📝 Content: {user_content}\n")

# Test both rules that user mentioned
print("📝 Testing nominalizations rule:")
from app.rules.nominalizations import check as nom_check
nom_results = nom_check(user_content)
print(f"  - Results: {len(nom_results)} issues")
for result in nom_results:
    print(f"    • {result}")

print("\n📝 Testing readability rule (fixed):")
from app.rules.readability_rules import check as read_check
read_results = read_check(user_content)
print(f"  - Results: {len(read_results)} issues")
for result in read_results:
    print(f"    • {result}")

# Test title detection for the exact phrase
print("\n📝 Title detection tests:")
from app.rules.title_utils import is_title_or_heading

test_phrases = [
    "Generating the connector configuration",
    "Generating the connector configuration\nSome content here.",
]

for phrase in test_phrases:
    result = is_title_or_heading(phrase, user_content)
    print(f"  - '{phrase[:50]}...' -> Title: {result}")

# Test with different HTML structures that might cause issues
print(f"\n📝 Testing different HTML structures:")

test_cases = [
    # Case 1: H2 tag
    '<h2>Generating the connector configuration</h2><p>Content</p>',
    # Case 2: H1 tag  
    '<h1>Generating the connector configuration</h1><p>Content</p>',
    # Case 3: No HTML tags
    'Generating the connector configuration\nContent',
    # Case 4: Different content after
    '<h2>Generating the connector configuration</h2><p>This sentence has implementation and configuration words.</p>'
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\nCase {i}: {test_case[:60]}...")
    
    nom_results = nom_check(test_case)
    read_results = read_check(test_case)
    
    print(f"  - Nominalizations: {len(nom_results)} issues")
    for result in nom_results:
        print(f"    • {result}")
    
    print(f"  - Readability: {len(read_results)} issues")
    for result in read_results:
        print(f"    • {result}")
