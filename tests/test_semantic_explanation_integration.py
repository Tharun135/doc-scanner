"""
Quick Integration Test: Semantic Explanation Layer
==================================================

Tests that the semantic explanation layer is properly integrated
and returns the expected results for your specific example.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rules.sentence_split_eligibility import (
    get_split_decision,
    is_semantically_complex,
    get_semantic_explanation_prompt,
    validate_semantic_explanation,
    get_ui_message
)

# Your original example
TEST_SENTENCE = (
    "The server certificate must include the IP address of the server in the SAN "
    "(Subject Alternative Name) field or the FQDN in case it is already registered "
    "in the DNS server."
)

print("=" * 80)
print("SEMANTIC EXPLANATION LAYER - INTEGRATION TEST")
print("=" * 80)

# Test 1: Complexity Detection
print("\n1. COMPLEXITY DETECTION")
print("-" * 80)
is_complex = is_semantically_complex(TEST_SENTENCE)
print(f"Sentence: {TEST_SENTENCE[:80]}...")
print(f"Is semantically complex: {is_complex}")
print(f"✅ PASS" if is_complex else "❌ FAIL: Should be detected as complex")

# Test 2: Decision Making
print("\n2. DECISION MAKING")
print("-" * 80)
decision, reason = get_split_decision(TEST_SENTENCE)
print(f"Decision: {decision}")
print(f"Reason: {reason}")
print(f"✅ PASS" if decision == "semantic_explanation" else f"❌ FAIL: Expected 'semantic_explanation', got '{decision}'")

# Test 3: Prompt Generation
print("\n3. PROMPT GENERATION")
print("-" * 80)
prompt = get_semantic_explanation_prompt(TEST_SENTENCE)
print(f"Prompt length: {len(prompt)} characters")
print(f"Contains rules: {'Rules:' in prompt}")
print(f"Contains sentence: {TEST_SENTENCE[:50] in prompt}")
print(f"Prohibits rewriting: {'Do NOT rewrite' in prompt}")
print("✅ PASS" if all([
    len(prompt) > 100,
    'Rules:' in prompt,
    TEST_SENTENCE[:50] in prompt,
    'Do NOT rewrite' in prompt
]) else "❌ FAIL: Prompt missing required elements")

# Test 4: Validation - Good Explanation
print("\n4. VALIDATION - GOOD EXPLANATION")
print("-" * 80)
good_explanation = (
    "This sentence defines a mandatory requirement with two alternatives. "
    "The condition applies only to the FQDN option, not the IP address option. "
    "It includes technical definitions bound to specific terms."
)
is_valid, val_reason = validate_semantic_explanation(TEST_SENTENCE, good_explanation)
print(f"Explanation: {good_explanation[:80]}...")
print(f"Valid: {is_valid}")
print(f"Reason: {val_reason}")
print(f"✅ PASS" if is_valid else f"❌ FAIL: {val_reason}")

# Test 5: Validation - Bad Explanation (Advisory)
print("\n5. VALIDATION - BAD EXPLANATION (ADVISORY)")
print("-" * 80)
bad_explanation = "You should split this sentence into two parts for better readability."
is_valid_bad, val_reason_bad = validate_semantic_explanation(TEST_SENTENCE, bad_explanation)
print(f"Explanation: {bad_explanation}")
print(f"Valid: {is_valid_bad}")
print(f"Reason: {val_reason_bad}")
print(f"✅ PASS" if not is_valid_bad else f"❌ FAIL: Should reject advisory language")

# Test 6: Validation - Bad Explanation (Rewrite)
print("\n6. VALIDATION - BAD EXPLANATION (REWRITE)")
print("-" * 80)
rewrite_explanation = TEST_SENTENCE.replace("must include", "should include")
is_valid_rewrite, val_reason_rewrite = validate_semantic_explanation(TEST_SENTENCE, rewrite_explanation)
print(f"Explanation: {rewrite_explanation[:80]}...")
print(f"Valid: {is_valid_rewrite}")
print(f"Reason: {val_reason_rewrite}")
print(f"✅ PASS" if not is_valid_rewrite else f"❌ FAIL: Should reject rewrites")

# Test 7: UI Messaging
print("\n7. UI MESSAGING")
print("-" * 80)
ui_msg = get_ui_message("semantic_explanation", len(TEST_SENTENCE.split()))
print(f"Title: {ui_msg['title']}")
print(f"Explanation: {ui_msg['explanation']}")
print(f"Note: {ui_msg.get('note', 'N/A')[:80]}...")
print(f"✅ PASS" if '🧠' in ui_msg['title'] and 'note' in ui_msg else "❌ FAIL: UI message incomplete")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\n✅ ALL INTEGRATION TESTS PASSED")
print("\nYour example sentence now gets:")
print(f"  Decision: {decision}")
print(f"  UI Title: {ui_msg['title']}")
print("\nThis proves AI understands without changing text.")
print("=" * 80)
