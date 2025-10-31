#!/usr/bin/env python3
"""
Test improved AI response extraction.
"""

import requests
import json

def test_improved_extraction():
    """Test the improved extraction patterns."""
    
    print("🎯 TESTING IMPROVED EXTRACTION")
    print("=" * 35)
    
    test_cases = [
        {
            "name": "Passive Voice Test 1",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was uploaded by the user."
        },
        {
            "name": "Passive Voice Test 2", 
            "feedback": "passive voice detected by rule",
            "sentence": "The system can be configured by administrators."
        },
        {
            "name": "Direct Test - New Prompt",
            "feedback": "passive voice detected by rule",
            "sentence": "The report was reviewed by the manager."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Input: \"{test_case['sentence']}\"")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json=test_case,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                sources = result.get('sources', [])
                
                print(f"   Method: {method}")
                print(f"   Sources: {len(sources)}")
                print(f"   AI Response: \"{ai_answer[:100]}{'...' if len(ai_answer) > 100 else ''}\"")
                print(f"   Suggestion: \"{suggestion}\"")
                
                # Quality analysis
                if method == 'ollama_rag_direct':
                    print(f"   ✅ Using highest quality method")
                else:
                    print(f"   ⚠️ Method: {method}")
                
                if suggestion and suggestion != test_case['sentence']:
                    if len(suggestion) > 10:
                        print(f"   ✅ Meaningful suggestion generated")
                        
                        # Check if it looks like a proper active voice conversion
                        if "user upload" in suggestion.lower() or "administrator" in suggestion.lower() or "manager review" in suggestion.lower():
                            print(f"   ✅ Proper active voice conversion")
                        elif not suggestion.startswith("Writing issue detected"):
                            print(f"   👍 Custom suggestion (not fallback)")
                        else:
                            print(f"   ⚠️ Generic fallback response")
                    else:
                        print(f"   ⚠️ Suggestion is too short")
                else:
                    print(f"   ❌ No meaningful suggestion")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def test_direct_ollama_with_new_prompt():
    """Test the new prompt format directly."""
    
    print(f"\n🤖 DIRECT OLLAMA TEST - NEW PROMPT")
    print("=" * 40)
    
    new_prompt = """Convert this passive voice sentence to active voice:

PASSIVE: "The file was uploaded by the user."
ACTIVE: """
    
    print(f"📝 New Prompt Format:")
    print(f'   "{new_prompt}"')
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'tinyllama:latest',
            'prompt': new_prompt,
            'stream': False,
            'options': {
                'temperature': 0.1,
                'top_p': 0.8,
                'num_predict': 120,
                'num_ctx': 1500,
                'repeat_penalty': 1.1,
                'mirostat': 0
            }
        }, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            print(f"\n🤖 DIRECT RESPONSE:")
            print(f'   "{ai_response}"')
            
            # Test extraction on this response
            if ai_response:
                cleaned = ai_response.strip().replace('"', '')
                print(f"\n✅ CLEANED EXTRACTION:")
                print(f'   "{cleaned}"')
                
                if cleaned and len(cleaned) > 10 and cleaned != "The file was uploaded by the user.":
                    print(f"   ✅ Good extraction candidate!")
                else:
                    print(f"   ⚠️ May need more work")
            
        else:
            print(f"❌ Ollama error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_improved_extraction()
    test_direct_ollama_with_new_prompt()
