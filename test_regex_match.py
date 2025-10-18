import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector

sentence = 'With "SLMP Connector V2.0", with qc, qx is published which holds all the bits data: quality code, sub status, extended sub status, flags, and limit.'

print(f"Original: {sentence}")

# Test the improved passive voice correction
corrector = RuleSpecificCorrector()
result = corrector.fix_passive_voice(sentence)

print(f"Corrected: {result}")
print(f"Changed: {result != sentence}")
