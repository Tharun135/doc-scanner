#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_title_case_scenarios():
    """Test various scenarios that might produce title case"""
    
    test_cases = [
        # Original sentence variations
        "the system demonstrates the installation steps in the following video:",
        "The system demonstrates the installation steps in the following video:",
        
        # Passive voice versions that should be converted
        "The installation steps are demonstrated by the system in the following video:",
        "Installation steps are demonstrated in the following video:",
        
        # Other potential problematic cases
        "the file is published by the system",
        "configuration is stored in the database",
        "data is processed automatically"
    ]
    
    print("🔍 Testing Title Case Scenarios")
    print("=" * 70)
    
    corrector = RuleSpecificCorrector()
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\nCase {i}: {sentence}")
        print("-" * 70)
        
        # Test different rule types that might cause issues
        rule_types = ["passive_voice", "capitalization", "general"]
        
        for rule_type in rule_types:
            try:
                issue = {
                    "message": f"{rule_type} issue found",
                    "context": sentence,
                    "issue_type": rule_type
                }
                
                result = enhanced_enrich_issue_with_solution(issue)
                suggested_text = result.get("proposed_rewrite", sentence)
                
                # Check for title case
                words = suggested_text.split()
                title_case_count = 0
                for word in words:
                    if word and len(word) > 1 and word[0].isupper() and word[1:].islower():
                        title_case_count += 1
                
                # If more than 50% of words are title case, it's suspicious
                if len(words) > 1 and title_case_count / len(words) > 0.5:
                    print(f"  {rule_type}: ⚠️ TITLE CASE: {suggested_text}")
                elif suggested_text != sentence:
                    print(f"  {rule_type}: ✅ Changed: {suggested_text}")
                else:
                    print(f"  {rule_type}: → No change")
                    
            except Exception as e:
                print(f"  {rule_type}: ❌ ERROR: {e}")

if __name__ == "__main__":
    test_title_case_scenarios()
