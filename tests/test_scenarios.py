#!/usr/bin/env python3

# Test with more realistic document context
import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test with various scenarios
test_scenarios = [
    # Scenario 1: Just the admonition
    '!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.',
    
    # Scenario 2: Admonition with preceding text
    '''Some text before.

!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.

Some text after.''',
    
    # Scenario 3: Multiple lines with the admonition
    '''# Configuration

This section describes configuration.

!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.

Continue with  more  text  that  has  multiple  spaces.''',
    
    # Scenario 4: Different admonition types
    '''!!! warning "WARNING" This is a warning message.
!!! note "NOTE" This is a note message.
!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.
!!! tip "TIP" This is a tip message.''',
]

for i, scenario in enumerate(test_scenarios, 1):
    print(f"\n=== Scenario {i} ===")
    print(f"Content: {repr(scenario)}")
    
    results = check(scenario)
    print(f"Found {len(results)} suggestions:")
    for suggestion in results:
        print(f"  - {suggestion}")
