"""
Regression Test: State Invariant Enforcement

CRITICAL INVARIANT:
When semantic explanation is active, guidance must be silent.
These two states are mutually exclusive and must never overlap.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai_improvement import _generate_smart_suggestion

def test_state_invariant():
    """
    Test that semantic_explanation and guidance_only are mutually exclusive.
    
    This is a regression test to prevent the bug where:
    - decision = semantic_explanation
    - but UI renders reviewer_guidance
    """
    
    print("\n" + "="*80)
    print("STATE INVARIANT TEST")
    print("="*80)
    
    # Test sentence that should trigger semantic explanation
    sentence = (
        "The server certificate must include the IP address of the server "
        "in the SAN (Subject Alternative Names) certificate extension or "
        "the FQDN (Fully Qualified Domain Name) in case it is already "
        "registered in the DNS server."
    )
    
    feedback = "Consider breaking this long sentence (34 words) into shorter ones for better readability"
    
    result = _generate_smart_suggestion(feedback, sentence)
    
    # Extract state flags
    is_semantic = result.get("is_semantic_explanation", False)
    is_guidance = result.get("is_guidance_only", False)
    method = result.get("method", "")
    decision_type = result.get("decision_type", "")
    
    print(f"\n📊 Result State:")
    print(f"   is_semantic_explanation = {is_semantic}")
    print(f"   is_guidance_only = {is_guidance}")
    print(f"   method = {method}")
    print(f"   decision_type = {decision_type}")
    
    # CRITICAL INVARIANT: These must be mutually exclusive
    print(f"\n🔍 Invariant Checks:")
    
    # Check 1: Not both true
    both_true = is_semantic and is_guidance
    print(f"   ❌ Both states active: {both_true}")
    
    # Check 2: At least one is explicitly set
    neither_true = not is_semantic and not is_guidance
    print(f"   ⚠️  Neither state set: {neither_true}")
    
    # Check 3: Method matches state
    if is_semantic:
        method_matches = method == "semantic_explanation"
        print(f"   {'✅' if method_matches else '❌'} Method matches semantic state: {method_matches}")
    elif is_guidance:
        method_matches = method == "reviewer_guidance"
        print(f"   {'✅' if method_matches else '❌'} Method matches guidance state: {method_matches}")
    
    # Check 4: Decision type matches state
    if is_semantic:
        decision_matches = decision_type == "semantic_explanation"
        print(f"   {'✅' if decision_matches else '❌'} Decision type matches semantic state: {decision_matches}")
    elif is_guidance:
        decision_matches = decision_type == "guidance_only"
        print(f"   {'✅' if decision_matches else '❌'} Decision type matches guidance state: {decision_matches}")
    
    # PASS/FAIL
    print(f"\n{'='*80}")
    if both_true:
        print("❌ FAIL: INVARIANT VIOLATED")
        print("   Semantic explanation and guidance are both active!")
        print("   This is the exact bug that was fixed.")
        return False
    elif neither_true:
        print("⚠️  WARNING: Ambiguous state")
        print("   Neither state is explicitly set.")
        return False
    else:
        print("✅ PASS: State invariant enforced correctly")
        print("   Semantic explanation and guidance are mutually exclusive.")
        return True

if __name__ == "__main__":
    success = test_state_invariant()
    sys.exit(0 if success else 1)
