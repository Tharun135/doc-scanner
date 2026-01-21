"""
Integration Test: Verify semantic explanation wins in intelligent_ai_improvement

This tests the actual path the user's browser request takes.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.intelligent_ai_improvement import should_attempt_rewrite, get_enhanced_ai_suggestion

print("\n" + "="*80)
print("INTEGRATION TEST: intelligent_ai_improvement.py Flow")
print("="*80)

sentence = (
    "The server certificate must include the IP address of the server "
    "in the SAN (Subject Alternative Name) field or "
    "the FQDN in case it is already registered in the DNS server."
)

feedback = "Consider breaking this long sentence (34 words) into shorter ones for better readability"

# Step 1: Check eligibility
print("\n📊 Step 1: Eligibility Check")
can_rewrite, reason = should_attempt_rewrite(feedback, sentence)
print(f"   can_rewrite = {can_rewrite}")
print(f"   reason = {reason}")

if not can_rewrite:
    print("\n❌ FAIL: Eligibility check blocked semantic explanation")
    sys.exit(1)

if "semantic explanation" not in reason.lower():
    print("\n❌ FAIL: Reason doesn't indicate semantic explanation")
    print(f"   Expected: 'Complex logic warrants semantic explanation'")
    print(f"   Got: {reason}")
    sys.exit(1)

print("   ✅ Eligibility check passed with semantic explanation signal")

# Step 2: Get actual suggestion
print("\n📊 Step 2: Get Enhanced AI Suggestion")
result = get_enhanced_ai_suggestion(feedback, sentence)

method = result.get("method", "")
is_semantic = result.get("is_semantic_explanation", False)
is_guidance = result.get("is_guidance_only", False)
ai_answer = result.get("ai_answer", "")

print(f"   method = {method}")
print(f"   is_semantic_explanation = {is_semantic}")
print(f"   is_guidance_only = {is_guidance}")
print(f"   ai_answer = {ai_answer[:80]}...")

# Verification
print("\n🔍 Verification:")

success = True

if method != "semantic_explanation":
    print(f"   ❌ FAIL: method should be 'semantic_explanation', got '{method}'")
    success = False
else:
    print(f"   ✅ PASS: method is 'semantic_explanation'")

if not is_semantic:
    print(f"   ❌ FAIL: is_semantic_explanation should be True")
    success = False
else:
    print(f"   ✅ PASS: is_semantic_explanation is True")

if is_guidance:
    print(f"   ❌ FAIL: is_guidance_only should be False")
    success = False
else:
    print(f"   ✅ PASS: is_guidance_only is False")

# Check for hint leakage
forbidden = ["split this sentence", "one sentence for", "main concept"]
has_leakage = any(f.lower() in ai_answer.lower() for f in forbidden)

if has_leakage:
    print(f"   ❌ FAIL: ai_answer contains guidance hints")
    success = False
else:
    print(f"   ✅ PASS: ai_answer is clean (no guidance hints)")

print("\n" + "="*80)
if success:
    print("✅ SUCCESS: Semantic explanation path works correctly")
    print("\nKey Achievement:")
    print("  • Eligibility check signals semantic explanation")
    print("  • AI processes request (not blocked)")
    print("  • Semantic explanation branch activates")
    print("  • Guidance never generated")
    print("  • Clean terminal state returned")
    sys.exit(0)
else:
    print("❌ FAILURE: Semantic explanation path broken")
    sys.exit(1)
