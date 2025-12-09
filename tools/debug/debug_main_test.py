#!/usr/bin/env python3
"""
Debug the exact same way the main test works
"""

import sys
import os
sys.path.append('.')

test_doc = '''<h2>Basic Configuration</h2>
<p>This rule checks for several things in your document. You should avoid passive voice construction when possible. The implementation must be done carefully.</p>'''

print("🔍 Testing rules exactly like the main test...")

# Load rules exactly like the main test
from app.app import load_rules
rules = load_rules()

print(f"📊 Loaded {len(rules)} rules")

for i, rule in enumerate(rules, 1):
    rule_name = rule.__module__.split('.')[-1]
    if rule_name in ['vague_terms', 'passive_voice']:
        print(f"\n📝 Testing {rule_name}:")
        try:
            suggestions = rule(test_doc)
            issue_count = len(suggestions) if suggestions else 0
            print(f"  - Issues found: {issue_count}")
            for suggestion in (suggestions or []):
                print(f"    • {suggestion}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # Also test the module imports
        try:
            module = sys.modules[rule.__module__]
            print(f"  - Module: {module}")
            print(f"  - TITLE_UTILS_AVAILABLE: {getattr(module, 'TITLE_UTILS_AVAILABLE', 'Not found')}")
            print(f"  - has is_title_or_heading: {hasattr(module, 'is_title_or_heading')}")
        except Exception as e:
            print(f"  ❌ Module check error: {e}")
