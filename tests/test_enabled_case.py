import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector

# Test the "enabled" case specifically  
sentence = 'When the "Bulk Publish" is enabled, the JSON structure for tags metadata is as follows:'

print(f"Testing: {sentence}")

# Test Pattern 4 specifically
when_simple_pattern = r'(When\s+.+?),\s*(.+?)\s+(?:is|are)\s+(?:also\s+)?([a-zA-Z]+ed)(\s+.+)?'
when_simple_match = re.search(when_simple_pattern, sentence, re.IGNORECASE)

print(f"Pattern 4 matches: {bool(when_simple_match)}")
if when_simple_match:
    print(f"Groups: {when_simple_match.groups()}")

# Test with corrector
corrector = RuleSpecificCorrector()
result = corrector.fix_passive_voice(sentence)
print(f"Corrector result: {result}")
print(f"Changed: {result != sentence}")

# The issue might be that "is as follows" doesn't end with "ed"
# Let's check what passive constructions are in this sentence
print(f"\nPassive analysis:")
print(f"Contains 'is enabled': {'is enabled' in sentence}")
print(f"Contains 'is as follows': {'is as follows' in sentence}")
print(f"'enabled' ends with 'ed': {'enabled'.endswith('ed')}")
print(f"'follows' ends with 'ed': {'follows'.endswith('ed')}")
