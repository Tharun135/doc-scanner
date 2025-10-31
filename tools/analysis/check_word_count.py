#!/usr/bin/env python3
"""
Check word count of the test sentence
"""

sentence = "In Model Maker, navigate to the XSLT Transformer tab, click on the Open L5X File button, and select the PLC program file exported from RSLogix 5000 or, Studio 5000 in .L5X format."

words = sentence.split()
print(f"🔍 Sentence word count analysis:")
print(f"📝 Sentence: {sentence}")
print(f"📊 Word count: {len(words)} words")
print(f"📏 Threshold: 25 words")
print(f"🎯 Should trigger rule: {'YES' if len(words) > 25 else 'NO'}")

# Test just the long_sentence rule directly
import sys
import os
sys.path.append('.')

test_content = f'<p>{sentence}</p>'
print(f"\n🔍 Direct rule test:")
from app.rules.long_sentence import check as long_check
result = long_check(test_content)
print(f"📊 Long sentence rule result: {len(result)} issues")
for r in result:
    print(f"  • {r}")
