import json
try:
    import requests
    print("🔧 Testing Flask endpoint...")
    response = requests.post("http://127.0.0.1:5000/ai_suggestion", json={
        "feedback": "passive voice",
        "sentence": "This is a passive voice sentence that was written.",
        "document_type": "general",
        "option_number": 1
    }, timeout=10)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Method: {result.get('method', 'unknown')}")
    print(f"Suggestion: {result.get('suggestion', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
