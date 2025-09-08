#!/usr/bin/env python3
"""
Test the rewriter class directly with a simpler approach
"""
import os
import sys
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_raw_rewriter():
    print("🧪 Testing Raw Rewriter Implementation")
    print("=" * 50)
    
    text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    
    # Direct API call using the fixed logic
    system_prompt = "Rewrite this text to be clearer and easier to understand. Use simple, direct language. Keep the same meaning but make it easier to read."
    full_prompt = f"{system_prompt}\n\nOriginal text: {text}\n\nRewritten text:"
    
    payload = {
        "model": "phi3:mini",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.4,
            "top_p": 0.9,
            "num_predict": min(300, len(text) * 2),
            "num_ctx": 2048
        }
    }
    
    print(f"Original text: {text}")
    print(f"Full prompt being sent: {full_prompt[:150]}...")
    print()
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "").strip()
        
        print(f"✅ Raw API call successful!")
        print(f"Generated text: {generated_text}")
        print()
        
        # Check if text was actually rewritten
        if generated_text.strip() and generated_text.lower().strip() != text.lower().strip():
            print("🎉 Success! Text was rewritten!")
            return True
        else:
            print("❌ Text was not rewritten (identical or empty)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_raw_rewriter()
    if success:
        print("\n✅ Raw implementation works - issue must be in Flask app")
    else:
        print("\n❌ Raw implementation fails - issue is deeper")
