#!/usr/bin/env python3
"""
Test enhanced RAG with both Ollama and ChromaDB-only paths for passive voice
"""
import sys
import os
import unittest.mock
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_both_paths():
    """Test passive voice correction in both Ollama and ChromaDB-only paths"""
    
    issue = {
        "message": "Avoid passive voice in sentence",
        "context": 'With "SLMP Connector V2.0", with qc, qx is published which holds all the bits data: quality code, sub status, extended sub status, flags, and limit.',
        "issue_type": "passive-voice"
    }
    
    print(f"🔍 Testing Both Enhanced RAG Paths:")
    print(f"  Input: '{issue['context'][:80]}...'")
    print(f"  Feedback: '{issue['message']}'")
    
    # Test 1: Normal path (may use Ollama or ChromaDB-only depending on availability)
    print(f"\n1. Testing normal path:")
    result1 = enhanced_enrich_issue_with_solution(issue)
    print(f"   Method: {result1.get('method', 'Unknown')}")
    print(f"   Changed: {result1.get('proposed_rewrite', '') != issue['context']}")
    print(f"   Has passive voice: {'is published' in result1.get('proposed_rewrite', '')}")
    
    # Test 2: Force ChromaDB-only path by mocking Ollama timeout
    print(f"\n2. Testing ChromaDB-only path (mocked Ollama timeout):")
    with unittest.mock.patch('requests.post', side_effect=requests.exceptions.Timeout):
        result2 = enhanced_enrich_issue_with_solution(issue)
        print(f"   Method: {result2.get('method', 'Unknown')}")
        print(f"   Changed: {result2.get('proposed_rewrite', '') != issue['context']}")
        print(f"   Has passive voice: {'is published' in result2.get('proposed_rewrite', '')}")
    
    print(f"\n🎯 Overall Assessment:")
    print(f"   Both paths fixed passive voice: {('is published' not in result1.get('proposed_rewrite', '')) and ('is published' not in result2.get('proposed_rewrite', ''))}")

if __name__ == "__main__":
    test_both_paths()
