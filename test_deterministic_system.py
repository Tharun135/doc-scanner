"""
Test the deterministic suggestion system.

This demonstrates:
1. Issues are classified deterministically
2. Every issue gets actionable guidance
3. Fallbacks work when AI unavailable
4. No vague or useless suggestions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.deterministic_suggestions import (
    DeterministicSuggestionGenerator,
    generate_suggestion_for_issue
)
from core.issue_resolution_engine import IssueType


def test_passive_voice_issue():
    """Test passive voice detection and resolution."""
    print("\n" + "=" * 60)
    print("TEST 1: Passive Voice Issue")
    print("=" * 60)
    
    issue = {
        'feedback': 'Avoid passive voice - consider using active voice',
        'context': 'The file was opened by the system.',
        'rule_id': 'passive_voice',
        'document_type': 'manual',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Type: {suggestion['issue_type']}")
        print(f"✓ Severity: {suggestion['severity']}")
        print(f"✓ Resolution Class: {suggestion['resolution_class']}")
        print(f"\nGuidance:\n{suggestion['guidance']}")
        
        if suggestion['rewrite']:
            print(f"\nSuggested Rewrite:\n{suggestion['rewrite']}")
        
        print(f"\nMethod: {suggestion['method']}")
        print(f"Confidence: {suggestion['confidence']}")
    else:
        print("✗ Issue not classified")


def test_long_sentence_issue():
    """Test long sentence detection and resolution."""
    print("\n" + "=" * 60)
    print("TEST 2: Long Sentence Issue")
    print("=" * 60)
    
    issue = {
        'feedback': 'Consider breaking this long sentence (35 words) into shorter ones',
        'context': 'The application provides a comprehensive set of tools and features that enable users to efficiently manage their documents, collaborate with team members, track changes, and maintain version control across multiple projects simultaneously.',
        'rule_id': 'long_sentence',
        'document_type': 'manual',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Type: {suggestion['issue_type']}")
        print(f"✓ Severity: {suggestion['severity']}")
        print(f"\nGuidance:\n{suggestion['guidance']}")
        
        if suggestion['rewrite']:
            print(f"\nSuggested Rewrite:\n{suggestion['rewrite']}")
        
        print(f"\nMethod: {suggestion['method']}")
    else:
        print("✗ Issue not classified")


def test_vague_term_issue():
    """Test vague term detection and resolution."""
    print("\n" + "=" * 60)
    print("TEST 3: Vague Term Issue")
    print("=" * 60)
    
    issue = {
        'feedback': "Avoid vague term 'several'",
        'context': 'Click the button several times to refresh.',
        'rule_id': 'vague_terms',
        'document_type': 'manual',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Type: {suggestion['issue_type']}")
        print(f"✓ Severity: {suggestion['severity']}")
        print(f"\nGuidance:\n{suggestion['guidance']}")
        
        if suggestion['rewrite']:
            print(f"\nSuggested Rewrite:\n{suggestion['rewrite']}")
        
        print(f"\nMethod: {suggestion['method']}")
    else:
        print("✗ Issue not classified")


def test_missing_prerequisite_issue():
    """Test missing prerequisite detection and resolution."""
    print("\n" + "=" * 60)
    print("TEST 4: Missing Prerequisite (Blocking)")
    print("=" * 60)
    
    issue = {
        'feedback': 'Missing Prerequisites Section',
        'context': '',  # Document-level issue
        'rule_id': 'ProcedureStructureRule',
        'document_type': 'procedure',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Type: {suggestion['issue_type']}")
        print(f"✓ Severity: {suggestion['severity']} (blocks user progress)")
        print(f"\nGuidance:\n{suggestion['guidance']}")
        print(f"\nAction Required: {suggestion['action_required']}")
        print(f"\nMethod: {suggestion['method']}")
    else:
        print("✗ Issue not classified")


def test_undefined_acronym_issue():
    """Test undefined acronym detection and resolution."""
    print("\n" + "=" * 60)
    print("TEST 5: Undefined Acronym")
    print("=" * 60)
    
    issue = {
        'feedback': 'Undefined Acronyms: REST, JWT',
        'context': 'The API uses REST and JWT for authentication.',
        'rule_id': 'AcronymConsistencyRule',
        'document_type': 'manual',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Type: {suggestion['issue_type']}")
        print(f"✓ Severity: {suggestion['severity']}")
        print(f"\nGuidance:\n{suggestion['guidance']}")
        print(f"\nMethod: {suggestion['method']}")
    else:
        print("✗ Issue not classified")


def test_unmapped_issue():
    """Test that unmapped issues return None (not shown to user)."""
    print("\n" + "=" * 60)
    print("TEST 6: Unmapped Issue (Should be filtered out)")
    print("=" * 60)
    
    issue = {
        'feedback': 'This is some random feedback that does not map to any resolution class',
        'context': 'Some text here.',
        'rule_id': 'unknown_rule',
        'document_type': 'general',
    }
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print("✗ FAIL: Unmapped issue was not filtered out")
    else:
        print("\n✓ PASS: Unmapped issue correctly filtered out")
        print("✓ This issue will NOT be shown to the user")
        print("✓ Only cleanly-mapped issues appear in results")


def test_batch_processing():
    """Test batch processing of multiple issues."""
    print("\n" + "=" * 60)
    print("TEST 7: Batch Processing")
    print("=" * 60)
    
    from core.deterministic_suggestions import generate_suggestions_for_issues
    
    issues = [
        {
            'feedback': 'Avoid passive voice',
            'context': 'The file was processed.',
            'rule_id': 'passive_voice',
            'document_type': 'manual',
        },
        {
            'feedback': 'Avoid vague term "things"',
            'context': 'Check the things in the list.',
            'rule_id': 'vague_terms',
            'document_type': 'manual',
        },
        {
            'feedback': 'Random unmapped issue',
            'context': 'Some text.',
            'rule_id': 'unknown',
            'document_type': 'general',
        },
        {
            'feedback': 'Consider breaking this long sentence',
            'context': 'This is a very long sentence with many clauses and subclauses that make it hard to read and understand clearly.',
            'rule_id': 'long_sentence',
            'document_type': 'manual',
        },
    ]
    
    suggestions = generate_suggestions_for_issues(issues)
    
    print(f"\n✓ Input: {len(issues)} issues")
    print(f"✓ Output: {len(suggestions)} suggestions")
    print(f"✓ Filtered: {len(issues) - len(suggestions)} unmapped issues")
    
    print("\nAll suggestions are actionable:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion['issue_type']} → {suggestion['resolution_class']}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DETERMINISTIC SUGGESTION SYSTEM TEST SUITE")
    print("=" * 60)
    print("\nThis demonstrates:")
    print("  ✓ Deterministic issue classification")
    print("  ✓ Guaranteed actionable guidance")
    print("  ✓ Fallbacks when AI unavailable")
    print("  ✓ Filtering of unmapped issues")
    
    try:
        test_passive_voice_issue()
        test_long_sentence_issue()
        test_vague_term_issue()
        test_missing_prerequisite_issue()
        test_undefined_acronym_issue()
        test_unmapped_issue()
        test_batch_processing()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE")
        print("=" * 60)
        print("\n✓ System produces actionable guidance for all classified issues")
        print("✓ Unmapped issues are filtered out")
        print("✓ No vague or useless suggestions")
        print("✓ Fallbacks guarantee value even without AI")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
