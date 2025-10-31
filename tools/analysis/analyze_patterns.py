import re

# Test Case 1
sentence1 = 'When you deploy a project, the metadata is also published.'
print('Case 1 Analysis:')
print('Contains is published:', 'is published' in sentence1)
print('Contains is also published:', 'is also published' in sentence1)

# Test our current simple pattern
simple_pattern = r'^(.+?)\s+(?:is|was|are|were)\s+([a-zA-Z]+ed)(\s+.+)?$'
match1 = re.search(simple_pattern, sentence1, re.IGNORECASE)
print('Simple pattern matches:', bool(match1))

# Test modified pattern to handle 'also'
modified_pattern = r'^(.+?)\s+(?:is|was|are|were)\s+(?:also\s+)?([a-zA-Z]+ed)(\s+.+)?$'
match1_mod = re.search(modified_pattern, sentence1, re.IGNORECASE)
print('Modified pattern matches:', bool(match1_mod))
if match1_mod:
    print('Groups:', match1_mod.groups())

print()

# Test Case 2
sentence2 = 'When the "Bulk Publish" is enabled, the JSON structure for tags metadata is as follows:'
print('Case 2 Analysis:')
print('Contains is enabled:', 'is enabled' in sentence2)

match2 = re.search(simple_pattern, sentence2, re.IGNORECASE)
print('Simple pattern matches:', bool(match2))

match2_mod = re.search(modified_pattern, sentence2, re.IGNORECASE)
print('Modified pattern matches:', bool(match2_mod))
if match2_mod:
    print('Groups:', match2_mod.groups())
