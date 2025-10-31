#!/usr/bin/env python3
"""
Simple test to check what the AI is actually returning for passive voice conversions.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import requests
import json

def test_direct_ollama_responses():
    """Test what Ollama returns directly for passive voice conversion."""
    
    print("🧪 TESTING DIRECT OLLAMA RESPONSES")
    print("=" * 50)
    
    # Test sentences
    test_sentences = [
        "The available connectors are shown.",
        "Data is displayed in the dashboard.", 
        "Reports are generated automatically."
    ]
    
    for sentence in test_sentences:
        print(f"\n🔍 TESTING: {sentence}")
        print("-" * 30)
        
        # Simple prompt for passive voice conversion
        prompt = f"""Convert this passive voice sentence to active voice. Be very concise and brief.

Original: {sentence}

IMPROVED_SENTENCE: [Write the improved sentence here]
EXPLANATION: [Brief explanation in 5-10 words]"""

        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': 'phi3:latest',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'max_tokens': 100  # Limit response length
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                print(f"✅ AI RESPONSE: {ai_response}")
                
                # Check word count
                word_count = len(ai_response.split())
                print(f"📊 WORD COUNT: {word_count}")
                
                if word_count > 50:
                    print("❌ TOO VERBOSE (>50 words)")
                else:
                    print("✅ REASONABLE LENGTH")
                    
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 DIRECT TEST COMPLETE")

if __name__ == "__main__":
    test_direct_ollama_responses()