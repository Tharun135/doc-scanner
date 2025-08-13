import sys
sys.path.append('.')

print('Testing rules system directly...')

# Test the rule loading system
from app.rules import rule_manager

print('Available rules:')
for rule_name, rule in rule_manager.get_all_rules().items():
    print(f'  - {rule_name}: {rule.description}')
    
print()

# Test passive voice detection
test_sentence = 'The document was written by the team.'
print(f'Testing sentence: "{test_sentence}"')

# Apply rules
violations = rule_manager.check_sentence(test_sentence)
print(f'Violations found: {len(violations)}')

for violation in violations:
    print(f'  - Rule: {violation.rule_name}')
    print(f'    Type: {violation.category}') 
    print(f'    Message: {violation.message}')
    print(f'    Start: {violation.start_pos}, End: {violation.end_pos}')
