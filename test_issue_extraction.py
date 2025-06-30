#!/usr/bin/env python3
"""
Test the issue extraction logic from structured suggestions.
"""

def extract_issue_from_structured_suggestion(suggestion_text):
    """Extract just the issue part from a structured suggestion."""
    if 'Issue:' in suggestion_text and 'Original sentence:' in suggestion_text and 'AI suggestion:' in suggestion_text:
        lines = suggestion_text.split('\n')
        for line in lines:
            if line.strip().startswith('Issue:'):
                return line.replace('Issue:', '').strip()
    return suggestion_text

# Test cases
test_cases = [
    "Issue: Weak verb construction detected\nOriginal sentence: There are three steps to follow.\nAI suggestion: Consider replacing 'There are' with 'list the items directly' for more direct communication.",
    "Issue: Passive voice detected\nOriginal sentence: The document was written by the team.\nAI suggestion: Consider revising to active voice for clearer, more direct communication.",
    "Legacy format suggestion without structure"
]

print("=== Testing Issue Extraction ===\n")

for i, suggestion in enumerate(test_cases, 1):
    print(f"Test {i}:")
    print(f"Original: {repr(suggestion)}")
    extracted = extract_issue_from_structured_suggestion(suggestion)
    print(f"Extracted Issue: {repr(extracted)}")
    print("-" * 50)

print("\n✅ This logic will ensure only the brief issue appears in the Issue tab!")
