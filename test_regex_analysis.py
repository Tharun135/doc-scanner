#!/usr/bin/env python3

import re

# Test various sentences to see what triggers the regex
test_sentences = [
    "If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files.",
    "Visit example.com for more information.",
    "The file.txt contains important data.",
    "Go to www.google.com to search.",
    "Use https://github.com for version control.",
    "The space.to accommodate files is limited.",
    "Files.upload to the server quickly.",
    "Storage.space is running low.",
    "Message.appears when needed."
]

# The problematic regex
url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'

print("Testing URL regex pattern on various sentences:\n")

for i, sentence in enumerate(test_sentences, 1):
    urls_found = re.findall(url_pattern, sentence, flags=re.IGNORECASE)
    print(f"Test {i}:")
    print(f"  Sentence: {sentence[:80]}...")
    print(f"  URLs found: {urls_found}")
    
    # Check what the third part of the regex matches specifically
    third_pattern = r'[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
    third_matches = re.findall(third_pattern, sentence, flags=re.IGNORECASE)
    print(f"  Third pattern matches: {third_matches}")
    print()

print("=" * 60)
print("ANALYSIS:")
print("The third pattern '[^\\s<>\"']+\\.[a-z]{2,}' is too aggressive.")
print("It matches any word.letters combination, including:")
print("- file.txt, space.to, storage.space, etc.")
print("These are not URLs but get flagged as potential URLs.")
print()
print("SOLUTION: Make the pattern more specific to actual domains.")
