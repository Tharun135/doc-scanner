#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🔍 Testing Complete RAG Flow")
print("=" * 40)

try:
    from app.rules.rag_rule_helper import check_with_rag, detect_passive_voice_issues
    
    # Test content
    content = '<p>The document was written by John yesterday.</p>'
    
    print(f"Content: {content}")
    print()
    
    # Test using check_with_rag (the actual function used by passive_voice.py)
    rule_patterns = {
        'detect_function': detect_passive_voice_issues
    }
    
    fallback_suggestions = [
        "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'."
    ]
    
    print("🧪 Testing check_with_rag function:")
    results = check_with_rag(
        content=content,
        rule_patterns=rule_patterns,
        rule_name="passive_voice",
        fallback_suggestions=fallback_suggestions
    )
    
    print(f"📊 Results: {len(results)} suggestions")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result}")
        # Check for RAG indicators
        if isinstance(result, dict):
            method = result.get('method', 'unknown')
            print(f"      Method: {method}")
            if 'rag' in method.lower():
                print("      🟢 RAG-enhanced!")
            elif 'fallback' in method.lower():
                print("      🟡 Using fallback")
        elif isinstance(result, str):
            if 'rag' in result.lower() or 'gemini' in result.lower():
                print("      🟢 RAG-enhanced!")
            elif 'fallback' in result.lower() or 'legacy' in result.lower():
                print("      🟡 Using fallback")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
