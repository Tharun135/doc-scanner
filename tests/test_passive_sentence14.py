"""Test passive voice rule on Sentence 14"""
from app.rules import passive_voice

sentence = "You can migrate existing configurations of the SIMATIC S7 Connector when S7-1200/1500 was configured using the optimized S7 protocol."

result = passive_voice.check(sentence)

print("=" * 80)
print("TEST: Passive Voice Detection on Sentence 14")
print("=" * 80)
print(f"\nSentence: {sentence}")
print(f"\nNumber of issues found: {len(result)}")

for i, issue in enumerate(result, 1):
    print(f"\n--- Issue {i} ---")
    if isinstance(issue, dict):
        print(f"Decision Type: {issue.get('decision_type', 'MISSING')}")
        print(f"Rule: {issue.get('rule', 'MISSING')}")
        print(f"Message: {issue.get('message', 'MISSING')}")
        print(f"Reviewer Rationale: {issue.get('reviewer_rationale', 'MISSING')}")
    else:
        print(f"String issue: {issue}")

print("\n" + "=" * 80)
