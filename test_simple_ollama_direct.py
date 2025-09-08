#!/usr/bin/env python3
"""
Very simple direct Ollama API test to isolate the rewriter issue
"""
import requests
import json

def test_direct_ollama_call():
    print("🧪 Testing Direct Ollama API Call")
    print("=" * 50)
    
    text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    prompt = f"Rewrite this text to be clearer and easier to understand: {text}"
    
    print(f"Original text: {text}")
    print(f"Prompt: {prompt}\n")
    
    # Direct API call
    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 100
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            rewritten = result.get("response", "").strip()
            
            print(f"✅ API Response successful!")
            print(f"Original:  '{text}'")
            print(f"Rewritten: '{rewritten}'")
            
            if text.strip() == rewritten:
                print("❌ Text is identical - no rewriting occurred!")
            else:
                print("✅ Text was successfully rewritten!")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_direct_ollama_call()
