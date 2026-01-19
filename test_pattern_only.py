import re

# Test the modal passive pattern directly
original = 'The PROFINET IO Connector provides the raw data, and the analysis of the record data must be done by the client.'

print("="*70)
print("TESTING MODAL PASSIVE PATTERN (IMPROVED)")
print("="*70)

print(f"\n📝 Original:")
print(f'"{original}"')

# NEW Pattern: More precise - starts with "the" to avoid matching across clauses
pattern = r'\bthe\s+([\w\s]+?)\s+must\s+be\s+done\s+by\s+the\s+(\w+)'
replacement = r'the \2 must do the \1'

match = re.search(pattern, original, re.IGNORECASE)
if match:
    print(f"\n✓ Pattern matched!")
    print(f"  Full match: '{match.group(0)}'")
    print(f"  Group 1 (object): '{match.group(1)}'")
    print(f"  Group 2 (actor): '{match.group(2)}'")
    
    # Check for clause boundaries in the match
    if ', and ' in match.group(0) or ', but ' in match.group(0):
        print("  ⚠️ Match crosses clause boundary - skipping")
    else:
        rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
        rewritten = re.sub(r'\s+', ' ', rewritten).strip()  # Clean up spaces
        rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
        
        print(f"\n🔄 Rewritten:")
        print(f'"{rewritten}"')
        
        if 'must be done' not in rewritten.lower():
            print("\n✅ Passive construction removed!")
        if 'the client must' in rewritten.lower():
            print("✅ Active voice with clear actor!")
else:
    print("\n❌ Pattern did not match!")
    
print("\n" + "="*70)

# Test other modal passive patterns
test_cases = [
    "The configuration must be done by the user.",
    "The file can be opened by the system.",
    "The settings should be configured by the admin.",
    "Data must be sent by the client.",
]

print("\nTesting other modal passive examples:")
for test in test_cases:
    print(f"\nOriginal: {test}")
    
    # Try modal patterns
    patterns = [
        (r'([\w\s]+?)\s+must\s+be\s+done\s+by\s+the\s+([\w\s]+)', r'the \2 must do \1'),
        (r'([\w\s]+?)\s+can\s+be\s+opened\s+by\s+the\s+([\w\s]+)', r'the \2 can open \1'),
        (r'([\w\s]+?)\s+should\s+be\s+configured\s+by\s+the\s+([\w\s]+)', r'the \2 should configure \1'),
        (r'([\w\s]+?)\s+must\s+be\s+sent\s+by\s+the\s+([\w\s]+)', r'the \2 must send \1'),
    ]
    
    for pat, rep in patterns:
        if re.search(pat, test, re.IGNORECASE):
            result = re.sub(pat, rep, test, count=1, flags=re.IGNORECASE)
            result = re.sub(r'\s+', ' ', result)
            print(f"Rewritten: {result}")
            break
