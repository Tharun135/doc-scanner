#!/usr/bin/env python3
"""
Test the full enhanced RAG system with improved passive voice correction
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_enhanced_rag_passive_voice():
    """Test the enhanced RAG system with passive voice issue"""
    
    # Test case: Complex passive voice
    issue = {
        "message": "Avoid passive voice in sentence",
        "context": 'With "SLMP Connector V2.0", with qc, qx is published which holds all the bits data: quality code, sub status, extended sub status, flags, and limit.',
        "issue_type": "passive-voice"
    }
    
    print(f"🔍 Testing Enhanced RAG with Improved Passive Voice:")
    print(f"  Input: '{issue['context']}'")
    print(f"  Feedback: '{issue['message']}'")
    
    try:
        result = enhanced_enrich_issue_with_solution(issue)
        
        print(f"  Method: {result.get('method', 'Unknown')}")
        print(f"  Proposed Rewrite: '{result.get('proposed_rewrite', '')}'")
        print(f"  Solution Text: '{result.get('solution_text', '')[:100]}...'")
        print(f"  Confidence: {result.get('confidence', 'Unknown')}")
        
        # Check if it actually fixed the passive voice
        original = issue['context']
        rewritten = result.get('proposed_rewrite', '')
        changed = rewritten != original
        has_passive = 'is published' in rewritten
        
        print(f"  ✅ Changed from original: {changed}")
        print(f"  ✅ Removed passive voice: {not has_passive}")
        print(f"  🎯 Overall Success: {changed and not has_passive}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_rag_passive_voice()
