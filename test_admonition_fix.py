#!/usr/bin/env python3

# Quick test for admonition exclusion in grammar rules
import sys
sys.path.append('.')

from app.rules.grammar_rules import check

# Test content with admonition that has multiple spaces
test_content = """
!!! info "NOTICE" These values are derived during the XSLT Transformation step in Model Maker.

This is a normal sentence with  multiple spaces that should be flagged.
"""

print("Testing admonition exclusion...")
results = check(test_content)

print(f"Found {len(results)} suggestions:")
for suggestion in results:
    print(f"- {suggestion}")

# Expected: Should only flag the normal sentence, not the admonition line
