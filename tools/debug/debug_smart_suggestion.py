import sys
sys.path.insert(0, 'app')
from ai_improvement import _generate_smart_suggestion
import re

test_sentence = 'LoRaWAN tags are made available in the Databus after you have selected the corresponding option for selected tags.'
feedback = 'Avoid passive voice in sentence'

print('Debug: _generate_smart_suggestion patterns')
print('=' * 50)
print(f'Original: {test_sentence}')
print(f'Feedback: {feedback}')

feedback_lower = feedback.lower()
print(f'Feedback lower: {feedback_lower}')

# Check if it matches passive voice detection
passive_keywords = ["was", "were", "been", "is being", "are being", "is displayed", "are displayed", "is shown", "are shown"]
has_passive_keywords = any(word in test_sentence.lower() for word in passive_keywords)
print(f'Has passive keywords: {has_passive_keywords}')
print(f'Contains "passive": {"passive" in feedback_lower}')

# Check the specific pattern
pattern_match = re.search(r"(?i)(.+?)\s+are\s+made\s+available", test_sentence)
print(f'Pattern match for "are made available": {pattern_match}')
if pattern_match:
    print(f'Matched groups: {pattern_match.groups()}')

# Call the function
result = _generate_smart_suggestion(feedback, test_sentence)
print(f'Result: {result}')