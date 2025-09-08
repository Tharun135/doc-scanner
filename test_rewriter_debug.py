#!/usr/bin/env python3
"""
Test the rewriter improvements calculation specifically
"""

import sys
import os
import requests

# Test directly without imports
def test_rewriter_api():
    print("🧪 Testing Rewriter API Directly")
    print("=" * 50)
    
    test_text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    
    print(f"Original text: {test_text}")
    print(f"Length: {len(test_text)} characters")
    
    # Test the Flask endpoint directly
    url = "http://127.0.0.1:5000/document-rewrite"
    
    payload = {
        "content": test_text,
        "mode": "simplicity",
        "audience": "general"
    }
    
    try:
        print(f"\n🔄 Calling rewriter API...")
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n📈 API Response:")
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            print(f"Original: {result.get('original_content', 'N/A')[:100]}...")
            print(f"Rewritten: {result.get('rewritten_content', 'N/A')[:100]}...")
            
            improvements = result.get('improvements', {})
            print(f"\n📊 Improvements:")
            for metric, data in improvements.items():
                if isinstance(data, dict):
                    print(f"  {metric}:")
                    print(f"    Before: {data.get('before', 'N/A')}")
                    print(f"    After: {data.get('after', 'N/A')}")
                    print(f"    Change: {data.get('improvement', 'N/A')}")
                else:
                    print(f"  {metric}: {data}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    test_rewriter_api()
