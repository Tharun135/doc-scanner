#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_user_specific_example():
    """Test the specific example provided by user"""
    
    # Your exact example
    test_sentence = "The system demonstrates the installation steps in the following video:"
    
    print("🎯 Testing User's Specific Example")
    print("=" * 60)
    print(f"Input: {test_sentence}")
    print("-" * 60)
    
    corrector = RuleSpecificCorrector()
    
    # Test direct rule-specific correction
    direct_result = corrector.fix_passive_voice(test_sentence)
    print(f"Direct Result: {direct_result}")
    
    # Test capitalization
    cap_result = corrector.fix_capitalization(test_sentence)
    print(f"Capitalization Result: {cap_result}")
    
    # Test through enhanced RAG integration
    try:
        issue = {
            "message": "Writing issue found",
            "context": test_sentence,
            "issue_type": "passive_voice"
        }
        
        rag_result = enhanced_enrich_issue_with_solution(issue)
        suggested_text = rag_result.get("proposed_rewrite", test_sentence)
        print(f"RAG Result: {suggested_text}")
        
        # Check for title case issues
        words = suggested_text.split()
        improperly_capitalized = []
        
        for i, word in enumerate(words):
            # Skip first word (should be capitalized)
            if i == 0:
                continue
            # Skip proper nouns and articles/prepositions that should be lowercase
            if word and word[0].isupper() and word.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'system', 'installation', 'steps', 'video']:
                improperly_capitalized.append(word)
        
        if improperly_capitalized:
            print(f"⚠️ TITLE CASE DETECTED: {improperly_capitalized}")
        else:
            print("✅ Capitalization looks correct")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_user_specific_example()
