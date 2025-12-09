#!/usr/bin/env python3

import sys
sys.path.append('.')

from app.rules.passive_voice import check

# Test various admonition scenarios
test_scenarios = [
    # Scenario 1: Simple admonition
    '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',
    
    # Scenario 2: Admonition in context
    '''# Configuration

!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.

This sentence should be flagged because it is written in passive voice.''',
    
    # Scenario 3: Multiple admonitions
    '''!!! warning "WARNING" This message was sent to alert users.
!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.
!!! tip "TIP" The settings can be configured by administrators.

Normal text that was written in passive voice should be flagged.''',
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n=== Scenario {i} ===")
    print(f"Content:\n{scenario}")
    
    results = check(scenario)
    print(f"\nFound {len(results)} passive voice suggestions:")
    for suggestion in results:
        print(f"  - {suggestion}")
