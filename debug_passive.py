"""
Debug the passive voice detection
"""
sentence = "The Time, Description, and Comments columns are fixed and cannot be removed."
feedback = "Avoid passive voice in sentence"

print("🔧 Debugging passive voice detection...")
print(f"Original: {sentence}")
print(f"Feedback: {feedback}")
print()
print("Checks:")
print(f"  'columns are fixed and cannot be removed' in sentence.lower(): {'columns are fixed and cannot be removed' in sentence.lower()}")
print(f"  'passive voice' in feedback.lower(): {'passive voice' in feedback.lower()}")

# Expected output
expected = "The system fixes the Time, Description, and Comments columns and prevents their removal."
print(f"\nExpected: {expected}")
