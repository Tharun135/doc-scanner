import sys
sys.path.insert(0, 'app')
from ai_improvement import _generate_smart_suggestion

test_sentence = 'LoRaWAN tags are made available in the Databus after you have selected the corresponding option for selected tags.'
feedback = 'Avoid passive voice in sentence'

print('Testing _generate_smart_suggestion')
print('=' * 50)
print(f'Original: {test_sentence}')

result = _generate_smart_suggestion(feedback, test_sentence)
if result:
    print(f'Suggestion: {result.get("suggestion", "No suggestion")}')
    print(f'Method: {result.get("method", "Unknown")}')
    print(f'Success: {result.get("success", False)}')
    if result.get('suggestion') != test_sentence:
        print('SUCCESS: Passive voice was converted!')
    else:
        print('ISSUE: Sentence was not converted')
else:
    print('No result returned')