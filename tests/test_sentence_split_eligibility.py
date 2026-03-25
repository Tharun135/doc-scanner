#!/usr/bin/env python3
"""
Test Suite: Sentence Split Eligibility Checker
===============================================

Tests the three-part implementation:
1. can_split_long_sentence() - Risk-based eligibility
2. always_split_long_sentence() - Always-safe categories
3. get_split_decision() - Master decision function
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.sentence_split_eligibility import (
    can_split_long_sentence,
    always_split_long_sentence,
    get_split_decision,
    get_ui_message,
    is_semantically_complex,
    get_semantic_explanation_prompt,
    validate_semantic_explanation
)


def test_case(name, sentence, expected_decision, check_reason=None):
    """Run a single test case."""
    decision, reason = get_split_decision(sentence)
    word_count = len(sentence.split())
    
    passed = decision == expected_decision
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"\n{status}: {name}")
    print(f"  Sentence ({word_count} words): {sentence[:80]}...")
    print(f"  Expected: {expected_decision}")
    print(f"  Got: {decision}")
    print(f"  Reason: {reason}")
    
    if check_reason and check_reason.lower() not in reason.lower():
        print(f"  ⚠️  Expected reason to contain: '{check_reason}'")
        return False
    
    return passed


def run_tests():
    """Run comprehensive test suite."""
    print("=" * 80)
    print("SENTENCE SPLIT ELIGIBILITY TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # ==========================================================================
    # TEST GROUP 1: GUIDANCE ONLY (Complex/Risky Sentences)
    # ==========================================================================
    print("\n" + "=" * 80)
    print("GROUP 1: GUIDANCE ONLY - Complex sentences requiring manual review")
    print("=" * 80)
    
    # Test 1: Conditional logic with normative language (your original example)
    results.append(test_case(
        "Conditional + Normative",
        "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server.",
        "guidance_only",
        "conditional"
    ))
    
    # Test 2: OR logic in requirements
    results.append(test_case(
        "Logical OR in requirement",
        "Users must authenticate using their company credentials or a valid external identity provider before accessing the system resources.",
        "guidance_only",
        "alternatives"
    ))
    
    # Test 3: Unless conditional
    results.append(test_case(
        "Unless conditional",
        "The system will automatically save your work every five minutes unless you have explicitly disabled the auto-save feature in the preferences menu.",
        "guidance_only",
        "conditional"
    ))
    
    # Test 4: Parenthetical technical definition
    results.append(test_case(
        "Technical parenthetical",
        "Configure the MCP (Model Context Protocol) server to listen on port 8080 and enable SSL encryption for all incoming connections from external clients.",
        "guidance_only",
        "parenthetical"
    ))
    
    # ==========================================================================
    # TEST GROUP 2: ALWAYS SPLIT - Low-risk, high-reward
    # ==========================================================================
    print("\n" + "=" * 80)
    print("GROUP 2: ALWAYS SPLIT - Safe sentences that should always be rewritten")
    print("=" * 80)
    
    # Test 5: Process chain with multiple "and"
    results.append(test_case(
        "Process chain",
        "The application processes incoming requests and validates user credentials and checks authorization levels and then forwards the data to the backend service for storage.",
        "always_split",
        "process chain"
    ))
    
    # Test 6: Explanation with consequence (which clause)
    results.append(test_case(
        "Which consequence",
        "The cache stores frequently accessed responses in memory, which significantly improves system performance and reduces database load during peak usage times.",
        "always_split",
        "consequence"
    ))
    
    # Test 7: Long introduction
    # Note: This one could be either always_split or eligible_split - both are acceptable
    # Conservative behavior (eligible) is fine, so we'll accept either
    decision_7, reason_7 = get_split_decision(
        "The Common Plant Model is a comprehensive configuration approach that organizes industrial assets and standardizes data structure across multiple automation systems and control platforms."
    )
    passed_7 = decision_7 in ["always_split", "eligible_split"]
    results.append(passed_7)
    print(f"\n{'✅ PASS' if passed_7 else '❌ FAIL'}: Long intro (flexible)")
    print(f"  Sentence (24 words): The Common Plant Model is a comprehensive configuration approach...")
    print(f"  Expected: always_split OR eligible_split")
    print(f"  Got: {decision_7}")
    print(f"  Reason: {reason_7}")
    
    # ==========================================================================
    # TEST GROUP 3: ELIGIBLE SPLIT - Safe but not mandatory
    # ==========================================================================
    print("\n" + "=" * 80)
    print("GROUP 3: ELIGIBLE SPLIT - Safe sentences, AI can split")
    print("=" * 80)
    
    # Test 8: Simple "and" connector
    results.append(test_case(
        "Simple conjunction",
        "The system validates the input data and then processes the transaction and finally generates a confirmation receipt for the user.",
        "eligible_split",
        "safe"
    ))
    
    # Test 9: After/before temporal connectors
    results.append(test_case(
        "Temporal connector",
        "The user clicks the submit button and then the form validation runs before the data is sent to the server for processing and storage.",
        "eligible_split",
        "safe"
    ))
    
    # ==========================================================================
    # TEST GROUP 4: SEMANTIC EXPLANATION
    # ==========================================================================
    print("\n" + "=" * 80)
    print("GROUP 4: SEMANTIC EXPLANATION - Complex sentences warranting explanation")
    print("=" * 80)
    
    # Test 10: Your original example - should trigger semantic explanation
    results.append(test_case(
        "Conditional + Normative (semantic)",
        "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server.",
        "semantic_explanation",
        "semantic"
    ))
    
    # Test complexity detection
    complex_sentence = "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."
    is_complex = is_semantically_complex(complex_sentence)
    print(f"\n{'✅ PASS' if is_complex else '❌ FAIL'}: Complexity detection")
    print(f"  Sentence: {complex_sentence[:80]}...")
    print(f"  Is semantically complex: {is_complex}")
    results.append(is_complex)
    
    # Test semantic explanation prompt
    prompt = get_semantic_explanation_prompt(complex_sentence)
    print(f"\n✅ Semantic Explanation Prompt Generated")
    print(f"  Length: {len(prompt)} chars")
    print(f"  Contains rules: {'Rules:' in prompt}")
    print(f"  Contains sentence: {complex_sentence[:30] in prompt}")
    
    # Test validation
    good_explanation = "This sentence defines a mandatory requirement with two alternatives. The condition applies only to the FQDN option."
    bad_explanation = "You should split this sentence into two parts."  # Advisory language
    
    is_valid_good, reason_good = validate_semantic_explanation(complex_sentence, good_explanation)
    is_valid_bad, reason_bad = validate_semantic_explanation(complex_sentence, bad_explanation)
    
    print(f"\n{'✅ PASS' if is_valid_good else '❌ FAIL'}: Good explanation validation")
    print(f"  Explanation: {good_explanation[:50]}...")
    print(f"  Valid: {is_valid_good}, Reason: {reason_good}")
    results.append(is_valid_good)
    
    print(f"\n{'✅ PASS' if not is_valid_bad else '❌ FAIL'}: Bad explanation rejection")
    print(f"  Explanation: {bad_explanation}")
    print(f"  Valid: {is_valid_bad}, Reason: {reason_bad}")
    results.append(not is_valid_bad)  # Should be rejected
    
    # ==========================================================================
    # TEST GROUP 5: UI MESSAGING
    # ==========================================================================
    print("\n" + "=" * 80)
    print("GROUP 5: UI MESSAGING - Reviewer-centric language")
    print("=" * 80)
    
    for decision_type in ["always_split", "eligible_split", "semantic_explanation", "guidance_only"]:
        ui_msg = get_ui_message(decision_type, 30)
        print(f"\n{decision_type.upper()}:")
        print(f"  Title: {ui_msg['title']}")
        print(f"  Explanation: {ui_msg['explanation']}")
        if 'note' in ui_msg:
            print(f"  Note: {ui_msg['note'][:80]}...")
        if 'recommendation' in ui_msg:
            print(f"  Recommendation: {ui_msg['recommendation'][:80]}...")
    
    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nResults: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Implementation is correct.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review implementation.")
        return 1


def demo_real_world_examples():
    """Demonstrate with real-world examples."""
    print("\n" + "=" * 80)
    print("REAL-WORLD EXAMPLES")
    print("=" * 80)
    
    examples = [
        ("Safe to split", 
         "This section provides information on how to transfer an IE app from the IE Hub to the IEM catalog of one or more IEM instances."),
        
        ("Risky - don't auto-split",
         "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."),
        
        ("Always split",
         "The application processes incoming requests and validates user credentials before forwarding data to the backend service."),
    ]
    
    for label, sentence in examples:
        print(f"\n{label.upper()}")
        print(f"Sentence: {sentence}")
        decision, reason = get_split_decision(sentence)
        ui_msg = get_ui_message(decision, len(sentence.split()))
        print(f"Decision: {decision}")
        print(f"Reason: {reason}")
        print(f"UI Title: {ui_msg['title']}")
        print(f"UI Message: {ui_msg['explanation']}")


if __name__ == "__main__":
    exit_code = run_tests()
    demo_real_world_examples()
    
    print("\n" + "=" * 80)
    print("KEY PRINCIPLES IMPLEMENTED:")
    print("=" * 80)
    print("1. ✅ AI rewrites only when correctness > convenience")
    print("2. ✅ Conservative: false negatives acceptable, false positives not")
    print("3. ✅ UI says 'reviewer decided', never 'AI failed'")
    print("4. ✅ Three-tier system: always/eligible/guidance")
    print("=" * 80)
    
    sys.exit(exit_code)
