#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_user_cases_final():
    """Final test of user's specific cases through the full enhanced RAG system"""
    
    user_cases = [
        "When you deploy a project, the metadata is also published.",
        "When the 'Bulk Publish' is enabled, the JSON structure for tags metadata is as follows:"
    ]
    
    print("🎯 Final Test of User's Specific Cases")
    print("=" * 60)
    
    for i, sentence in enumerate(user_cases, 1):
        print(f"\nCase {i}: {sentence}")
        print("-" * 60)
        
        try:
            # Test with enhanced RAG
            issue = {
                "message": f"Passive voice found",
                "context": sentence,
                "issue_type": "passive_voice"
            }
            
            result = enhanced_enrich_issue_with_solution(issue)
            
            suggested_text = result.get("proposed_rewrite", sentence)
            print(f"Enhanced RAG Result: {suggested_text}")
            
            # Check if it's different from original
            if suggested_text.strip() != sentence.strip():
                print("✅ FIXED: Sentence was successfully converted!")
            else:
                print("❌ NOT FIXED: Sentence remains unchanged")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_user_cases_final()
