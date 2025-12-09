#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_ollama_issue():
    """Test if we can reproduce title case from Ollama responses"""
    import requests
    import json
    
    # Test sentence that user reported
    test_sentence = "The system demonstrates the installation steps in the following video:"
    
    print("🔍 Testing Direct Ollama for Title Case Issue")
    print("=" * 60)
    print(f"Input: {test_sentence}")
    print("-" * 60)
    
    # Try a few different prompts to see if any produce title case
    prompts = [
        f'Convert this passive voice to active voice: "{test_sentence}"',
        f'Fix this writing issue: passive voice found\nORIGINAL: "{test_sentence}"\nIMPROVED:',
        f'Based on writing rules, fix passive voice in: "{test_sentence}"',
        f'Rewrite in active voice: "{test_sentence}"'
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}: {prompt[:50]}...")
        
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={
                    'model': 'phi3:mini',
                    'prompt': prompt,
                    'stream': False
                }, 
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get('response', '').strip()
                print(f"Response: {ollama_response}")
                
                # Check for title case
                words = ollama_response.split()
                title_case_words = []
                for word in words:
                    if word and len(word) > 1 and word[0].isupper() and word[1:].islower():
                        # Skip expected capitalized words
                        if word.lower() not in ['the', 'a', 'an', 'system', 'installation', 'steps', 'video']:
                            title_case_words.append(word)
                
                if len(title_case_words) > len(words) * 0.4:  # More than 40% title case
                    print(f"⚠️ TITLE CASE DETECTED: {title_case_words}")
                else:
                    print("✅ Normal capitalization")
            else:
                print(f"❌ Ollama error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_direct_ollama_issue()
