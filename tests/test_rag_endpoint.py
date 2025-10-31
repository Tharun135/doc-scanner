import requests
import json
import time

print("🔧 Testing RAG suggestions through Flask API...")

# Wait a moment for server to be ready
time.sleep(2)

url = "http://127.0.0.1:5000/ai_suggestion"
data = {
    "feedback": "Check use of adverb: 'precisely'",  # More specific feedback like the user mentioned
    "sentence": "You can precisely extract the necessary information from designated PLCs, enhancing operational efficiency and clarity.",
    "document_type": "technical",
    "option_number": 1
}

try:
    print(f"Making request to {url}...")
    response = requests.post(url, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'N/A')}")
        print(f"AI Answer: {result.get('ai_answer', 'N/A')}")
        
        if 'local_rag' in result.get('method', ''):
            print("✅ RAG system is working!")
        else:
            print("❌ Still using fallback")
    else:
        print(f"Error response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server - make sure it's running on port 5000")
except Exception as e:
    print(f"❌ Error: {e}")
