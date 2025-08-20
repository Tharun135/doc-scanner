#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from app.rules.title_utils import is_title_or_heading

# Test various title patterns
test_cases = [
    ('This is a Very Long Title That Would Normally Be Flagged for Being Too Long', '<h1>This is a Very Long Title That Would Normally Be Flagged for Being Too Long</h1>'),
    ('CONFIGURATION SETTINGS', '<h2>CONFIGURATION SETTINGS</h2>'),
    ('getting started guide', '<h3>getting started guide</h3>'),
    ('Introduction', '<p>Introduction</p>'),
    ('Getting Started', '<p>Getting Started</p>'),
    ('INSTALLATION GUIDE', '<p>INSTALLATION GUIDE</p>'),
    ('1. Configuration', '<p>1. Configuration</p>'),
    ('This is a regular sentence.', '<p>This is a regular sentence.</p>')
]

print('🧪 Title Detection Test:')
for text, html in test_cases:
    result = is_title_or_heading(text, html)
    status = '✅ TITLE' if result else '❌ NOT TITLE'
    print(f'{status}: "{text[:40]}..."')
