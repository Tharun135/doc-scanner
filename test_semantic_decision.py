"""Test semantic explanation decision for certificate sentence"""

from app.rules.sentence_split_eligibility import get_split_decision

# The 34-word certificate sentence
sentence = "The server certificate must include the IP address of the server in the SAN (Subject Alternative Name) field or the FQDN in case it is already registered in the DNS server."

print(f"Sentence length: {len(sentence.split())} words")
print(f"\nSentence: {sentence}\n")

# Get the decision
decision, reason = get_split_decision(sentence)

print(f"Decision: {decision}")
print(f"Reason: {reason}")

# Expected: semantic_explanation
# Reason: Has conditional " in case ", has " or ", has technical parenthetical
assert decision == "semantic_explanation", f"Expected 'semantic_explanation', got '{decision}'"
print("\n✅ Test passed! Decision is semantic_explanation")
