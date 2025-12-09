#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector

def test_new_when_pattern():
    """Test the new Pattern 5 for handling passive voice in When clauses"""
    corrector = RuleSpecificCorrector()
    
    # Test cases
    test_cases = [
        "When you deploy a project, the metadata is also published.",
        "When the 'Bulk Publish' is enabled, the JSON structure for tags metadata is as follows:",
        "When a file is uploaded, the content is processed.",
        "When the user is authenticated, the data is retrieved.",
    ]
    
    print("Testing new Pattern 5 for passive voice in When clauses:\n")
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"Case {i}: {sentence}")
        
        # Test direct correction
        corrected = corrector.fix_passive_voice(sentence)
        print(f"Direct: {corrected}")
        
        print("-" * 80)

if __name__ == "__main__":
    test_new_when_pattern()
