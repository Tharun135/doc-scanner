import sys
sys.path.append('d:/doc-scanner')
from app.ai_improvement import EnhancedAISuggestionEngine

# Test the AI improvement engine directly
engine = EnhancedAISuggestionEngine()

# Test possibility context
possibility_feedback = "Modal verb usage - 'may' for possibility"
possibility_sentence = "Loading the tags may take some time depending on the size of the export file."

print("=== Testing Possibility Context ===")
print(f"Feedback: {possibility_feedback}")
print(f"Sentence: {possibility_sentence}")

# This should test our new logic
result = engine._generate_general_improvement_suggestion(possibility_feedback, possibility_sentence)
print(f"AI Suggestion: {result}")
print()

# Test permission context
permission_feedback = "Use of 'may' for permission context"
permission_sentence = "You may access the settings page."

print("=== Testing Permission Context ===")
print(f"Feedback: {permission_feedback}")
print(f"Sentence: {permission_sentence}")

result2 = engine._generate_general_improvement_suggestion(permission_feedback, permission_sentence)
print(f"AI Suggestion: {result2}")
