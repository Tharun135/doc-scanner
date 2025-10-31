#!/usr/bin/env python3
"""
Test the enhanced RAG integration with Ollama unavailable to force ChromaDB-only path
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chromadb_only_path():
    """Test capitalization fix in ChromaDB-only path by simulating Ollama unavailable"""
    
    import unittest.mock
    import requests
    from enhanced_rag_integration import enhanced_enrich_issue_with_solution
    
    # Test case: Capitalization issue
    issue = {
        "message": "Start sentences with a capital letter.",
        "context": "it is in ISO 8601 Zulu format.",
        "issue_type": "style"
    }
    
    print(f"🔍 Testing ChromaDB-only path (simulating Ollama timeout):")
    print(f"  Input: '{issue['context']}'")
    print(f"  Feedback: '{issue['message']}'")
    
    # Mock Ollama to always timeout to force ChromaDB-only path
    with unittest.mock.patch('requests.post', side_effect=requests.exceptions.Timeout):
        try:
            result = enhanced_enrich_issue_with_solution(issue)
            
            print(f"  Method: {result.get('method', 'Unknown')}")
            print(f"  Proposed Rewrite: '{result.get('proposed_rewrite', '')}'")
            print(f"  Solution Text: '{result.get('solution_text', '')}'")
            print(f"  Confidence: {result.get('confidence', 'Unknown')}")
            
            # Check if it's properly capitalized
            proposed_rewrite = result.get('proposed_rewrite', '')
            is_capitalized = proposed_rewrite and proposed_rewrite[0].isupper()
            is_changed = proposed_rewrite != issue['context']
            no_improved_prefix = not proposed_rewrite.startswith("Improved:")
            method_is_chromadb_only = result.get('method') == 'enhanced_rag_chromadb_only'
            
            print(f"  ✅ Method is ChromaDB-only: {method_is_chromadb_only}")
            print(f"  ✅ Capitalized: {is_capitalized}")
            print(f"  ✅ Changed from original: {is_changed}")
            print(f"  ✅ No 'Improved:' prefix: {no_improved_prefix}")
            
            # Test success
            success = is_capitalized and is_changed and no_improved_prefix and method_is_chromadb_only
            print(f"  🎯 ChromaDB-only Success: {success}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_chromadb_only_path()
