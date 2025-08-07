#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🔍 Testing Passive Voice Detection")
print("=" * 40)

try:
    from app.rules.rag_rule_helper import detect_passive_voice_issues
    
    # Test content
    content = '<p>The document was written by John yesterday.</p>'
    text_content = 'The document was written by John yesterday.'
    
    print(f"HTML content: {content}")
    print(f"Text content: {text_content}")
    print()
    
    # Test detection
    issues = detect_passive_voice_issues(content, text_content)
    
    print(f"📊 Detected issues: {len(issues)}")
    for i, issue in enumerate(issues):
        print(f"  {i+1}. {issue}")
    
    # Test individual patterns
    import re
    print(f"\n🧪 Testing individual patterns:")
    test_patterns = [
        r'\bwas\s+written\b',
        r'\bwas\s+\w+ed\b',
        r'\bis\s+\w+ed\b',
    ]
    
    for pattern in test_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        print(f"  Pattern '{pattern}': {'✅ MATCH' if match else '❌ NO MATCH'}")
        if match:
            print(f"    Found: '{match.group()}'")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
