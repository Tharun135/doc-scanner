#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🔍 Testing RAG Suggestion Formatting")
print("=" * 40)

try:
    from app.rules.passive_voice import check
    
    # Test content with passive voice
    content = '<p>The document was written by John yesterday.</p>'
    
    print(f"Testing content: {content}")
    print()
    
    results = check(content)
    print(f"📊 Results: {len(results)} suggestions")
    
    for i, result in enumerate(results):
        print(f"\n--- Suggestion {i+1} ---")
        if isinstance(result, dict):
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Rule: {result.get('rule', 'unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            print(f"Text: {result.get('text', 'No text')}")
        else:
            print(f"String result: {result}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
