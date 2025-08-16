import sys
sys.path.append('.')
from app.app import load_rules

# Test rules loading
print('Testing rules loading...')
rules = load_rules()
print(f'Rules loaded: {len(rules)}')

# Test rule execution
test_text = 'microsoft should be capitalized.'
print(f'Testing rules on: "{test_text}"')

for i, rule in enumerate(rules):
    try:
        result = rule(test_text)
        if result:
            print(f'Rule {i}: {result}')
        else:
            print(f'Rule {i}: No issues')
    except Exception as e:
        print(f'Rule {i}: ERROR - {e}')
