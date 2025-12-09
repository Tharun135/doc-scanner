#!/usr/bin/env python3
"""
Debug the specific failing cases from user examples
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def debug_user_cases():
    """Debug the specific cases that are failing for the user"""
    
    test_cases = [
        {
            "name": "User Case 1 - Failed",
            "input": "When you deploy a project, the metadata is also published.",
            "feedback": "Avoid passive voice in sentence"
        },
        {
            "name": "User Case 2 - Worked", 
            "input": 'When the "Bulk Publish" is enabled, the JSON structure for tags metadata is as follows:',
            "feedback": "Avoid passive voice in sentence"
        }
    ]
    
    corrector = RuleSpecificCorrector()
    
    print("🔍 Debugging User's Specific Failing Cases")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print(f"   Input: '{case['input']}'")
        
        # Test direct rule correction
        direct_result = corrector.fix_passive_voice(case['input'])
        print(f"   Direct: '{direct_result}'")
        print(f"   Direct Changed: {direct_result != case['input']}")
        
        # Test pattern matching step by step
        import re
        
        # Test When pattern
        when_pattern = r'When\s+(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed),\s*(.+?)(?:is|are)\s+([a-zA-Z]+ed)'
        when_match = re.search(when_pattern, case['input'], re.IGNORECASE)
        print(f"   When pattern match: {bool(when_match)}")
        
        # Test by pattern
        by_pattern = r'(.+?)\s+(?:is|was|are|were)\s+([a-zA-Z]+ed)\s+by\s+(.+)'
        by_match = re.search(by_pattern, case['input'], re.IGNORECASE)
        print(f"   By pattern match: {bool(by_match)}")
        
        # Test complex pattern
        complex_pattern = r'(With\s+.+?),\s*(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed)(\s+.+)?'
        complex_match = re.search(complex_pattern, case['input'], re.IGNORECASE)
        print(f"   Complex pattern match: {bool(complex_match)}")
        
        # Test simple pattern
        simple_pattern = r'^(.+?)\s+(?:is|was|are|were)\s+([a-zA-Z]+ed)(\s+.+)?$'
        simple_match = re.search(simple_pattern, case['input'], re.IGNORECASE)
        print(f"   Simple pattern match: {bool(simple_match)}")
        if simple_match:
            print(f"      Object: '{simple_match.group(1)}'")
            print(f"      Verb: '{simple_match.group(2)}'")
            print(f"      Rest: '{simple_match.group(3) or ''}'")
            print(f"      Object word count: {len(simple_match.group(1).split())}")
            print(f"      Starts with 'With': {simple_match.group(1).startswith('With ')}")
        
        # Test via enhanced RAG
        print(f"   Testing via Enhanced RAG:")
        issue = {
            "message": case['feedback'],
            "context": case['input'],
            "issue_type": "passive-voice"
        }
        
        try:
            rag_result = enhanced_enrich_issue_with_solution(issue)
            rag_output = rag_result.get('proposed_rewrite', '')
            print(f"   RAG Result: '{rag_output}'")
            print(f"   RAG Changed: {rag_output != case['input']}")
            print(f"   RAG Method: {rag_result.get('method', 'Unknown')}")
        except Exception as e:
            print(f"   RAG Error: {e}")

if __name__ == "__main__":
    debug_user_cases()
