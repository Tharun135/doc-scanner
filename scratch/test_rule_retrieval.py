import sys
sys.path.insert(0, 'd:/doc-scanner')
from app.rag.rule_vectorstore import get_rule_vectorstore
store = get_rule_vectorstore()
print('Rules in store:', store.count())
tests = [
    'The configuration should be updated by the user.',
    'Click on the Save button.',
    'The system shall start automatically.',
    'I will configure the system.',
    'Simply configure the settings.',
]
for sent in tests:
    results = store.retrieve_rules(sent, top_k=3)
    top = [(r['rule_id'], round(r['score'],3)) for r in results]
    print(f'  Sent: {sent[:45]}')
    print(f'  Top rules: {top}')
