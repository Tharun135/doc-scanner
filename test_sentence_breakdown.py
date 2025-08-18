#!/usr/bin/env python3

import re

# The problematic sentence broken into parts to test
sentence = "If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files."

# Split into words and test combinations
words = sentence.split()
print("Testing word combinations from the problematic sentence:\n")

url_pattern = r'[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'

# Test individual words
print("Individual words that might match:")
for word in words:
    if re.match(url_pattern, word, flags=re.IGNORECASE):
        print(f"  '{word}' matches the URL pattern")

print()

# Test adjacent word combinations (in case punctuation affects it)
print("Testing adjacent word combinations:")
for i in range(len(words) - 1):
    combo = words[i] + "." + words[i + 1]
    if re.match(url_pattern, combo, flags=re.IGNORECASE):
        print(f"  '{combo}' would match if combined")

print()

# Test specific combinations that might occur
test_combinations = [
    "space.to",
    "message.appears", 
    "error.message",
    "storage.space",
    "files.chosen",
    "upload.consume",
    "available.space",
    "accommodate.the",
    "selected.files"
]

print("Testing specific combinations:")
for combo in test_combinations:
    if re.match(url_pattern, combo, flags=re.IGNORECASE):
        print(f"  '{combo}' matches the URL pattern")

print()
print("=" * 60)
print("It's possible the sentence gets processed differently in the full app,")
print("or there might be HTML artifacts affecting the text extraction.")
