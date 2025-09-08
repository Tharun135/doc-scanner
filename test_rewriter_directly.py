#!/usr/bin/env python3
"""
Direct test of the Ollama Rewriter class without API
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rewriter.ollama_rewriter import OllamaRewriter

def test_direct_rewriter():
    print("🧪 Testing Ollama Rewriter Class Directly")
    print("=" * 50)
    
    text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    print(f"Original text: {text}")
    print(f"Length: {len(text)} characters\n")
    
    # Test direct rewriter
    rewriter = OllamaRewriter()
    
    # Test _ollama_generate method directly
    print("🔄 Testing _ollama_generate method directly...")
    prompt = "Rewrite this text to be clearer and easier to understand: " + text
    response = rewriter._ollama_generate(prompt)
    print(f"Direct _ollama_generate response: '{response}'\n")
    
    # Test rewrite_document method
    print("🔄 Testing rewrite_document method...")
    result = rewriter.rewrite_document(text, mode='simplicity')
    
    print(f"📈 Rewriter Result:")
    print(f"Success: {result.get('success', False)}")
    print(f"Original: {result.get('original_text', 'N/A')[:80]}...")  
    print(f"Rewritten: {result.get('rewritten_text', 'N/A')[:80]}...")
    
    if result.get('improvements'):
        print("\n📊 Improvements:")
        for metric, data in result['improvements'].items():
            print(f"  {metric}:")
            if isinstance(data, dict):
                before = data.get('before', 'N/A')
                after = data.get('after', 'N/A') 
                change = data.get('change', 'N/A')
                print(f"    Before: {before}")
                print(f"    After: {after}")
                print(f"    Change: {change}")
            else:
                print(f"    {data}")

if __name__ == "__main__":
    test_direct_rewriter()
