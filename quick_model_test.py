import requests
import json

# Test Ollama with exact model names
models_to_test = ["phi3:mini", "llama3:8b", "tinyllama:latest"]

for model in models_to_test:
    print(f"\n🧪 Testing {model}:")
    
    payload = {
        "model": model,
        "prompt": "Rewrite: 'The implementation of advanced methodologies necessitates understanding.' Make it simpler.",
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 30
        }
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        generated_text = result.get('response', '').strip()
        print(f"✅ Success: '{generated_text}'")
        
        if generated_text and generated_text != payload['prompt']:
            print("🎉 Model is working - text was rewritten!")
            break
        else:
            print("⚠️  Model returned empty or same text")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\nDone testing models.")
