"""
Regression Test: No Hint Leakage in Guidance

Tests that the anti-pattern identified by the user is eliminated:
❌ "ℹ️ Complex logic warrants semantic explanation" 
    appearing inside guidance text

This must NEVER happen. When guidance is shown, it must be clean
with no hints about semantic explanation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai_improvement import _generate_smart_suggestion

def test_no_hint_leakage():
    """
    Test that guidance text never contains semantic explanation hints.
    """
    
    print("\n" + "="*80)
    print("REGRESSION TEST: No Hint Leakage in Guidance")
    print("="*80)
    
    # Test sentence that could trigger semantic explanation
    sentence = (
        "The server certificate must include the IP address of the server "
        "in the SAN (Subject Alternative Name) field or "
        "the FQDN in case it is already registered in the DNS server."
    )
    
    feedback = "Consider breaking this long sentence (34 words) into shorter ones for better readability"
    
    print(f"\n📝 Test Sentence:")
    print(f"   {sentence[:80]}...")
    
    result = _generate_smart_suggestion(feedback, sentence)
    
    # Extract the content that will be displayed to user
    ai_answer = result.get("ai_answer", "")
    decision_type = result.get("decision_type", "")
    method = result.get("method", "")
    
    print(f"\n📊 Result:")
    print(f"   method = {method}")
    print(f"   decision_type = {decision_type}")
    print(f"   ai_answer = {ai_answer[:100]}...")
    
    # The FORBIDDEN patterns that must never appear in guidance
    forbidden_patterns = [
        "Complex logic warrants semantic explanation",
        "ℹ️ Complex logic",
        "semantic explanation",
        "warrants semantic"
    ]
    
    print(f"\n🔍 Checking for hint leakage...")
    
    leakage_found = False
    for pattern in forbidden_patterns:
        if pattern.lower() in ai_answer.lower():
            print(f"   ❌ LEAKAGE FOUND: '{pattern}' appears in ai_answer")
            leakage_found = True
        else:
            print(f"   ✅ Clean: '{pattern}' not found")
    
    # CRITICAL: If method is guidance, ai_answer must not mention semantic explanation
    if method == "reviewer_guidance":
        print(f"\n📋 Method is reviewer_guidance - checking for clean terminal state...")
        if any(pattern.lower() in ai_answer.lower() for pattern in forbidden_patterns):
            print(f"   ❌ FAIL: Guidance contains semantic explanation hints")
            print(f"   This is the anti-pattern that was fixed!")
            return False
        else:
            print(f"   ✅ PASS: Guidance is clean - no semantic hints")
    
    # Summary
    print(f"\n{'='*80}")
    if leakage_found:
        print("❌ FAIL: Hint leakage detected")
        print("\nThe Anti-Pattern:")
        print("  When guidance is shown, it must be silent about semantic explanation.")
        print("  Hints about other states = state leakage.")
        return False
    else:
        print("✅ PASS: No hint leakage detected")
        print("\nKey Invariant Enforced:")
        print("  Guidance text is clean - contains no hints about semantic explanation")
        return True

if __name__ == "__main__":
    success = test_no_hint_leakage()
    sys.exit(0 if success else 1)
