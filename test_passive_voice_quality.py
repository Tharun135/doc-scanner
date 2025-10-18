#!/usr/bin/env python3
"""
Comprehensive test of passive voice to active voice conversion quality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag.rule_specific_corrections import RuleSpecificCorrector
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

def test_passive_voice_quality():
    """Test passive voice conversion quality across different sentence types"""
    
    # Test cases covering different passive voice patterns
    test_cases = [
        {
            "name": "Simple 'is published'",
            "input": "The file is published.",
            "expected_contains": ["publishes", "system", "file"]
        },
        {
            "name": "Complex with prepositional phrase",
            "input": 'With "SLMP Connector V2.0", with qc, qx is published which holds all the bits data.',
            "expected_contains": ["system publishes", "qx"]
        },
        {
            "name": "'by' construction",
            "input": "The data is processed by the system.",
            "expected_contains": ["system processes", "data"]
        },
        {
            "name": "Multiple passive constructions",
            "input": "When the file is uploaded, the data is processed automatically.",
            "expected_contains": ["upload", "process"]
        },
        {
            "name": "Technical documentation style",
            "input": "The configuration is stored in the database.",
            "expected_contains": ["system stores", "configuration"]
        },
        {
            "name": "Past tense passive",
            "input": "The report was generated yesterday.",
            "expected_contains": ["generated", "report"]
        },
        {
            "name": "Plural passive",
            "input": "The files are uploaded to the server.",
            "expected_contains": ["upload", "files"]
        },
        {
            "name": "Embedded passive clause",
            "input": "The API endpoint, which is configured automatically, returns JSON data.",
            "expected_contains": ["configure", "endpoint"]
        }
    ]
    
    corrector = RuleSpecificCorrector()
    
    print("🔍 Passive Voice to Active Voice Conversion Quality Test")
    print("=" * 70)
    
    total_tests = len(test_cases)
    successful_conversions = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input:  '{test_case['input']}'")
        
        # Test direct rule-specific correction
        result = corrector.fix_passive_voice(test_case['input'])
        
        print(f"   Output: '{result}'")
        
        # Check if conversion was successful
        changed = result != test_case['input']
        has_passive_markers = any(marker in result.lower() for marker in [' is ', ' are ', ' was ', ' were '])
        
        # Check if expected elements are present
        contains_expected = all(
            any(expected.lower() in result.lower() for expected in test_case['expected_contains'])
            for expected in test_case['expected_contains']
        )
        
        # Overall quality assessment
        if changed and not has_passive_markers:
            quality = "Excellent ✅"
            successful_conversions += 1
        elif changed:
            quality = "Good 🟡" 
        else:
            quality = "Poor ❌"
            
        print(f"   Quality: {quality}")
        print(f"   Changed: {changed} | Passive removed: {not has_passive_markers}")
        
        # Test through full enhanced RAG system
        print(f"   Testing via Enhanced RAG:")
        issue = {
            "message": "Avoid passive voice in sentence",
            "context": test_case['input'],
            "issue_type": "passive-voice"
        }
        
        try:
            rag_result = enhanced_enrich_issue_with_solution(issue)
            rag_output = rag_result.get('proposed_rewrite', '')
            rag_changed = rag_output != test_case['input']
            print(f"   RAG Output: '{rag_output}'")
            print(f"   RAG Quality: {'Good ✅' if rag_changed else 'Poor ❌'}")
        except Exception as e:
            print(f"   RAG Error: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 SUMMARY:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful conversions: {successful_conversions}")
    print(f"   Success rate: {successful_conversions/total_tests*100:.1f}%")
    
    # Quality assessment
    if successful_conversions >= total_tests * 0.8:
        overall_quality = "Excellent 🌟"
    elif successful_conversions >= total_tests * 0.6:
        overall_quality = "Good 👍"
    elif successful_conversions >= total_tests * 0.4:
        overall_quality = "Fair 🤔"
    else:
        overall_quality = "Needs Improvement 🔧"
    
    print(f"   Overall Quality: {overall_quality}")
    
    return successful_conversions / total_tests

if __name__ == "__main__":
    test_passive_voice_quality()
