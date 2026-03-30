"""
Test the AI rewrite block rule for normative + conditional sentences.
"""

from app.intelligent_ai_improvement import (
    contains_normative_language,
    contains_conditional_or_alternative,
    blocks_ai_rewrite
)

def test_block_rule():
    """Test the block rule with various sentences."""
    
    test_cases = [
        {
            "sentence": "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server.",
            "expected_blocked": True,
            "reason": "Contains 'must' (normative) + 'or' and 'in case' (conditional/alternative)"
        },
        {
            "sentence": "You should use active voice for clearer writing.",
            "expected_blocked": False,
            "reason": "No normative language (should is not mandatory)"
        },
        {
            "sentence": "The system must authenticate users.",
            "expected_blocked": False,
            "reason": "Normative but no conditional/alternative"
        },
        {
            "sentence": "Use either method A or method B.",
            "expected_blocked": False,
            "reason": "Alternative but no normative language"
        },
        {
            "sentence": "Users shall provide either a password or a certificate if authentication is required.",
            "expected_blocked": True,
            "reason": "Contains 'shall' (normative) + 'either/or/if' (conditional/alternative)"
        },
        {
            "sentence": "The configuration must be set unless the default is acceptable.",
            "expected_blocked": True,
            "reason": "Contains 'must' (normative) + 'unless' (conditional)"
        }
    ]
    
    print("\n" + "="*80)
    print("AI REWRITE BLOCK RULE TEST")
    print("="*80)
    
    for i, test in enumerate(test_cases, 1):
        sentence = test["sentence"]
        expected = test["expected_blocked"]
        reason = test["reason"]
        
        has_normative = contains_normative_language(sentence)
        has_conditional = contains_conditional_or_alternative(sentence)
        is_blocked = blocks_ai_rewrite(sentence)
        
        status = "✅ PASS" if is_blocked == expected else "❌ FAIL"
        
        print(f"\n[Test {i}] {status}")
        print(f"Sentence: {sentence[:80]}...")
        print(f"Expected: {'BLOCKED' if expected else 'ALLOWED'}")
        print(f"Actual:   {'BLOCKED' if is_blocked else 'ALLOWED'}")
        print(f"Normative: {has_normative}, Conditional: {has_conditional}")
        print(f"Reason: {reason}")
    
    print("\n" + "="*80)
    print("Test complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_block_rule()
