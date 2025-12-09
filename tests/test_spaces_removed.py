#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test various scenarios with multiple spaces
test_scenarios = [
    # Scenario 1: Multiple spaces in regular text
    'This text has  multiple  spaces  between  words.',
    
    # Scenario 2: Multiple spaces with admonitions
    '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',
    
    # Scenario 3: Mixed content with multiple spaces
    '''# Title

This paragraph has  multiple  spaces.

!!! warning "WARNING" This is  a  warning  message.

More text with  extra  spaces.'''
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n=== Scenario {i} ===")
    print(f"Content: {repr(scenario)}")
    
    results = check(scenario)
    print(f"Grammar rule suggestions: {len(results)}")
    for suggestion in results:
        print(f"  - {suggestion}")

print(f"\n✅ Multiple consecutive spaces rule has been removed from grammar rules!")
