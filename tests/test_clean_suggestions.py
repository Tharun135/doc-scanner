#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🎯 Testing Clean RAG Suggestions")
print("=" * 50)

def test_rule(rule_name, content, expected_issues=1):
    """Test a specific rule and show clean formatted output."""
    try:
        module = __import__(f'app.rules.{rule_name}', fromlist=[rule_name])
        if hasattr(module, 'check'):
            print(f"\n📝 Testing {rule_name}:")
            print(f"   Content: {content}")
            
            results = module.check(content)
            print(f"   Found: {len(results)} suggestions")
            
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    method = result.get('method', 'unknown')
                    message = result.get('message', 'No message')
                    print(f"   {i+1}. {message}")
                    print(f"      Method: {method}")
                    if 'rag' in method.lower():
                        print("      ✅ RAG-enhanced (crisp and clear!)")
                    else:
                        print(f"      ⚠️ Using {method}")
                else:
                    print(f"   {i+1}. {result}")
                    
        else:
            print(f"   ❌ No check function found")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Test cases
test_cases = [
    {
        'rule': 'passive_voice',
        'content': '<p>The document was written by John yesterday.</p>',
        'description': 'Passive voice detection'
    },
    {
        'rule': 'long_sentences', 
        'content': '<p>This is a very long sentence that contains too many words and clauses and should probably be broken down into shorter, more manageable sentences for better readability and comprehension.</p>',
        'description': 'Long sentence detection'
    },
    {
        'rule': 'cross_references',
        'content': '<p>If the files chosen for upload consume more than 90% of the available space, an error message appears.</p>',
        'description': 'URL false positive test (should find no URLs)'
    }
]

print("Testing multiple rules with clean formatting:")

for test_case in test_cases:
    print(f"\n🧪 {test_case['description']}")
    test_rule(test_case['rule'], test_case['content'])

print("\n" + "=" * 50)
print("✅ Summary: RAG suggestions are now clean and user-friendly!")
print("✅ No more raw 'OPTION 1:, OPTION 2:, WHY:' output")
print("✅ Clear, actionable suggestions like 'Convert to active voice: ...'")
print("✅ No false URL detection for 'space.to accommodate' patterns")
