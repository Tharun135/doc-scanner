"""
Simple test to check if the user's Flask RAG is actually working
"""
import requests
import json

print("🔧 Testing Flask AI endpoint with improved suggestions...")

# Test data
data = {
    'feedback': 'Avoid passive voice in sentence',
    'sentence': 'Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.',
    'document_type': 'technical',
    'option_number': 1
}

try:
    # Test the actual running server (if any)
    response = requests.post('http://127.0.0.1:5000/ai_suggestion', json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Request successful!")
        print(f"Status: {response.status_code}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'none')}")
        
        if result.get('method') == 'local_rag' and 'Consider revising:' not in result.get('suggestion', ''):
            print("✅ RAG is working with intelligent suggestions!")
        else:
            print("❌ Still getting generic suggestions")
    else:
        print(f"❌ Request failed with status: {response.status_code}")
        print(f"Error: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Server not running - cannot test Flask API")
except Exception as e:
    print(f"❌ Error testing API: {e}")
