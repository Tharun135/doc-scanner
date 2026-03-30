"""
Test the click on fix
"""
import re

# Test the pattern
sentence = 'Click on "Convert".'
pattern = r"\bclick\s+on\b"
replacement = "click"

print(f"Original: {sentence}")
print(f"Pattern: {pattern}")

if re.search(pattern, sentence, re.IGNORECASE):
    result = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
    print(f"Result: {result}")
    print(f"Match found: YES")
else:
    print("Match found: NO")

# Test old pattern
old_pattern = r"\bclick on\b"
print(f"\n--- Testing old pattern ---")
print(f"Old pattern: {old_pattern}")
if re.search(old_pattern, sentence, re.IGNORECASE):
    result_old = re.sub(old_pattern, replacement, sentence, flags=re.IGNORECASE)
    print(f"Result: {result_old}")
    print(f"Match found: YES")
else:
    print("Match found: NO")
