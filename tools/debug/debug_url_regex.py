#!/usr/bin/env python3

import re

# Test the problematic sentence
test_sentence = "If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files."

print("Testing URL detection regex:\n")
print(f"Sentence: {test_sentence}")
print()

# The regex pattern from cross_references.py
url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'

print("Breaking down the regex pattern:")
print("1. https?://[^\\s<>\"']+  - matches http/https URLs")
print("2. www\\.[^\\s<>\"']+     - matches www. domains") 
print("3. [^\\s<>\"']+\\.[a-z]{2,}(?:/[^\\s<>\"']*)? - matches domain.ext patterns")
print()

urls_found = re.findall(url_pattern, test_sentence, flags=re.IGNORECASE)
print(f"URLs found: {urls_found}")
print()

# Test each part of the regex separately
parts = [
    r'https?://[^\s<>"\']+',
    r'www\.[^\s<>"\']+', 
    r'[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
]

for i, part in enumerate(parts, 1):
    matches = re.findall(part, test_sentence, flags=re.IGNORECASE)
    print(f"Part {i} matches: {matches}")

print()
print("=" * 60)
print("The problematic part is likely part 3 which matches any word followed by a dot and 2+ letters")

# Let's see what specific words trigger this
words = test_sentence.split()
for word in words:
    if re.match(r'[^\s<>"\']+\.[a-z]{2,}', word, flags=re.IGNORECASE):
        print(f"Word '{word}' matches the domain pattern")
