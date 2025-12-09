"""
Quick test of the simplified Flask server
"""
import requests
import json
import time

print("🔧 Testing simplified Flask server...")

# Test data matching your exact example
data = {
    'feedback': 'Avoid passive voice in sentence',
    'sentence': 'Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.',
    'document_type': 'technical',
    'option_number': 1
}

try:
    # Give the server a moment to fully start
    time.sleep(2)
    
    print("Making request to server...")
    response = requests.post('http://127.0.0.1:5001/ai_suggestion', json=data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"Status: {response.status_code}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'none')[:100]}...")
        
        # Check if we got intelligent suggestions
        suggestion = result.get('suggestion', '')
        if result.get('method') == 'local_rag' or result.get('method') == 'direct_rag':
            if 'Consider revising:' not in suggestion:
                print("✅ 🎉 RAG IS WORKING WITH INTELLIGENT SUGGESTIONS!")
            else:
                print("🔄 RAG method detected but still generic suggestion")
        else:
            print(f"ℹ️ Using method: {result.get('method')}")
    else:
        print(f"❌ Request failed with status: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server")
except Exception as e:
    print(f"❌ Error: {e}")
