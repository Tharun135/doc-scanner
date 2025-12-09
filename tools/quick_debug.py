#!/usr/bin/env python3
"""
Quick test to see why ollama_rag_direct stopped working.
"""

import requests

def quick_test():
    """Test a simple case that should definitely work."""
    
    print("🔍 QUICK TEST: Why ollama_rag_direct stopped working")
    print("=" * 50)
    
    # Simple test that worked before
    test_data = {
        'feedback': 'passive voice detected by rule',
        'sentence': 'The file was saved by the user.'
    }
    
    print(f"📝 Testing: {test_data}")
    
    try:
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            method = result.get('method', 'unknown')
            
            print(f"✅ Response: {method}")
            
            if method != 'ollama_rag_direct':
                print(f"❌ PROBLEM: Expected ollama_rag_direct, got {method}")
                print(f"   This suggests an error in the enrichment service")
                
                # Check if we can see the error
                ai_answer = result.get('ai_answer', '')
                print(f"   AI Answer: '{ai_answer[:100]}...'")
            else:
                print(f"✅ ollama_rag_direct is working fine")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
    
    print(f"\n💡 If ollama_rag_direct isn't working:")
    print(f"   1. There might be a syntax error in the enrichment service")
    print(f"   2. The ChromaDB collection might not be available")
    print(f"   3. Ollama service might not be responding")
    print(f"   4. Check the Flask terminal for error messages")
