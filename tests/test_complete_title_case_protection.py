#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_complete_title_case_protection():
    """Test the complete system with title case protection"""
    
    # Simulate title case issues that might come from various sources
    test_cases = [
        {
            "message": "Passive voice found",
            "context": "The System Demonstrates The Installation Steps In The Following Video:",
            "issue_type": "passive_voice"
        },
        {
            "message": "Capitalization issue",  
            "context": "the system demonstrates the installation steps in the following video:",
            "issue_type": "capitalization"
        },
        {
            "message": "Passive voice found",
            "context": "When You Deploy A Project, The Metadata Is Also Published.",
            "issue_type": "passive_voice"
        },
        {
            "message": "Writing issue",
            "context": "The File Is Published By The Application System.",
            "issue_type": "general"
        }
    ]
    
    print("🛡️ Complete System Title Case Protection Test")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nCase {i}: {test_case['context']}")
        print(f"Issue: {test_case['message']}")
        print("-" * 70)
        
        try:
            result = enhanced_enrich_issue_with_solution(test_case)
            suggested_text = result.get("proposed_rewrite", test_case["context"])
            
            print(f"Result: {suggested_text}")
            print(f"Method: {result.get('method', 'unknown')}")
            
            # Check if title case was fixed
            original_words = test_case["context"].split()
            result_words = suggested_text.split()
            
            # Count title case words in original vs result
            orig_title_count = sum(1 for w in original_words[1:] if w and len(w) > 2 and w[0].isupper() and w[1:].islower())
            result_title_count = sum(1 for w in result_words[1:] if w and len(w) > 2 and w[0].isupper() and w[1:].islower())
            
            if orig_title_count > result_title_count + 2:  # Significant reduction in title case
                print("✅ TITLE CASE PROTECTED: Inappropriate capitalization fixed")
            elif suggested_text != test_case["context"]:
                print("✅ CONTENT CHANGED: Text was improved")
            else:
                print("→ No change made")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print()

if __name__ == "__main__":
    test_complete_title_case_protection()
