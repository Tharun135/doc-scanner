#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

from app.rules.concise_simple_words import check

# Test case for the URL highlighting issue
test_text = """
The syntax for the URL is as follows: https://<IP_IED>/webrh/<path_to_mediafile>
"""

print("Testing URL sentence highlighting:\n")

suggestions = check(test_text)

print(f"Test sentence: {test_text.strip()}")
print(f"Number of suggestions: {len(suggestions)}")
print()

for suggestion in suggestions:
    print(f"Suggestion: {suggestion}")
    print()

print("=" * 60)
print("ANALYSIS:")
print("This sentence contains special characters that might cause highlighting issues:")
print("- Angle brackets: < >")
print("- Colons: :")
print("- Forward slashes: /")
print("- Underscores: _")
print("- URL protocol: https://")
