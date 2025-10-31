#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_capitalization_issue():
    """Test the capitalization issue reported by user"""
    
    # Test sentences that might produce title case
    test_cases = [
        "the system demonstrates the installation steps in the following video:",
        "The installation is demonstrated by the system.",
        "The file is published by the application.",
        "Installation steps are shown in the video."
    ]
    
    print("🔍 Testing Capitalization Issues")
    print("=" * 60)
    
    corrector = RuleSpecificCorrector()
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\nCase {i}: {sentence}")
        print("-" * 60)
        
        # Test direct rule-specific correction
        direct_result = corrector.fix_passive_voice(sentence)
        print(f"Direct Result: {direct_result}")
        
        # Test through enhanced RAG integration
        try:
            issue = {
                "message": "Passive voice found",
                "context": sentence,
                "issue_type": "passive_voice"
            }
            
            rag_result = enhanced_enrich_issue_with_solution(issue)
            suggested_text = rag_result.get("proposed_rewrite", sentence)
            print(f"RAG Result: {suggested_text}")
            
            # Check for title case issues
            words = suggested_text.split()
            title_case_words = [word for word in words if word and word[0].isupper() and len(word) > 1 and word[1:].islower() and word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']]
            
            if len(title_case_words) > 2:  # More than expected (sentence start + proper nouns)
                print(f"⚠️ POTENTIAL TITLE CASE ISSUE: {title_case_words}")
            else:
                print("✅ Capitalization looks normal")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()

if __name__ == "__main__":
    test_capitalization_issue()
