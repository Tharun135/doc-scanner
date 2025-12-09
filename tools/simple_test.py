import requests
import json
import time

print("🔧 Testing improved RAG suggestions...")

url = "http://127.0.0.1:5000/ai_suggestion"
data = {
    "feedback": "Avoid passive voice in sentence",
    "sentence": "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.",
    "document_type": "technical",
    "option_number": 1
}

print(f"Request: {data}")

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Method: {result.get('method')}")
        print(f"Suggestion: {result.get('suggestion')}")
        
        if 'Click the button' in result.get('suggestion', '') or 'Use Date and Time' in result.get('suggestion', ''):
            print("✅ RAG system is generating intelligent suggestions!")
        else:
            print("❌ Still getting generic suggestions")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
