import requests
import json

print("🔧 Making AI suggestion request...")

url = "http://127.0.0.1:5000/ai_suggestion"
data = {
    "feedback": "passive voice",
    "sentence": "This is a passive voice sentence that was written.",
    "document_type": "general",
    "option_number": 1
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
