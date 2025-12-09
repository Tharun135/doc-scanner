#!/usr/bin/env python3
"""
Test the LLM API directly
"""
import requests

def test_ollama_direct():
    print("🤖 Testing Direct Ollama API")
    
    test_case = {
        "feedback": "Avoid passive voice in sentence: 'Tags are only defined for sensors.'",
        "sentence": "Tags are only defined for sensors."
    }
    
    prompt = f"""You are a professional technical writing assistant. Your task is to rewrite the given sentence to fix the specific writing issue.

WRITING ISSUE: {test_case["feedback"]}
ORIGINAL SENTENCE: "{test_case["sentence"]}"

Instructions:
- Provide ONLY the improved sentence, nothing else
- Fix the specific issue mentioned in the feedback
- Keep the meaning intact
- Make it clear, concise, and professional
- Use active voice when possible
- Follow technical writing best practices

REWRITTEN SENTENCE:"""

    try:
        ollama_url = "http://localhost:11434/api/generate"
        response = requests.post(ollama_url, json={
            'model': 'phi3:mini',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'top_p': 0.9,
                'num_predict': 100
            }
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            suggestion = result['response'].strip()
            
            print(f"✅ LLM Response: {suggestion}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama_direct()
