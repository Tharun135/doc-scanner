"""
Test the complete semantic explanation flow in ai_improvement.py
"""
import sys
sys.path.insert(0, 'D:\\doc-scanner')

from app.ai_improvement import _generate_smart_suggestion

# Your exact example
sentence = (
    "The server certificate must include the IP address of the server in the SAN "
    "(Subject Alternative Name) field or the FQDN in case it is already registered "
    "in the DNS server."
)
feedback = "Consider breaking this long sentence (34 words) into shorter ones for better readability"

print("=" * 80)
print("TESTING SEMANTIC EXPLANATION FLOW")
print("=" * 80)
print(f"\nSentence: {sentence[:80]}...")
print(f"Feedback: {feedback}")

result = _generate_smart_suggestion(feedback, sentence)

print("\n" + "=" * 80)
print("RESULT:")
print("=" * 80)
print(f"Method: {result.get('method')}")
print(f"Decision Type: {result.get('decision_type')}")
print(f"Decision Reason: {result.get('decision_reason')}")
print(f"Is Semantic Explanation: {result.get('is_semantic_explanation')}")
print(f"Is Guidance Only: {result.get('is_guidance_only')}")

if 'semantic_explanation' in result:
    print(f"\n✅ Semantic Explanation Generated:")
    print(f"   {result['semantic_explanation']}")
else:
    print(f"\n❌ No semantic_explanation field in result")

print(f"\nAI Answer: {result.get('ai_answer')[:100]}...")

print("\n" + "=" * 80)
if result.get('method') == 'semantic_explanation' and result.get('is_semantic_explanation'):
    print("✅ SUCCESS: Semantic explanation tier activated correctly")
else:
    print(f"❌ FAIL: Expected method='semantic_explanation', got '{result.get('method')}'")
print("=" * 80)
