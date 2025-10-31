#!/usr/bin/env python3

# Test how the JavaScript word splitting would work in Python
test_sentence = "The syntax for the URL is as follows: https://<IP_IED>/webrh/<path_to_mediafile>"

print("Original sentence:")
print(test_sentence)
print()

# Simulate JavaScript: sentence.split(/\s+/).filter(word => word.length > 2)
words = [word for word in test_sentence.split() if len(word) > 2]
print("Words extracted (length > 2):")
for i, word in enumerate(words):
    print(f"{i}: '{word}'")
print()

# Check for problematic characters
print("Potential regex issues:")
for word in words:
    # Characters that need escaping in regex
    special_chars = ['[', ']', '(', ')', '{', '}', '.', '*', '+', '?', '^', '$', '|', '\\']
    if any(char in word for char in special_chars):
        print(f"Word '{word}' contains regex special characters")
    if '<' in word or '>' in word:
        print(f"Word '{word}' contains angle brackets")
    if ':' in word:
        print(f"Word '{word}' contains colon")
    if '/' in word:
        print(f"Word '{word}' contains forward slash")
print()

# Test the regex escaping
import re
print("Escaped words for regex:")
for word in words:
    escaped = re.escape(word)
    print(f"'{word}' -> '{escaped}'")
