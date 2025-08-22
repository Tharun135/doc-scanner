"""
Test AI suggestion endpoint directly to understand the exact flow from UI
"""
import requests
import json

# Test data matching your example
test_data = {
    "feedback": "Avoid using ALL CAPS for emphasis. Use bold or italics instead.",
    "sentence": "The configuration of SIMATIC S7+ Connector offers flexibility through manual configuration or file importation.",
    "document_type": "technical",
    "writing_goals": ["clarity", "conciseness"]
}

print("🧪 Testing AI Suggestion Endpoint Directly")
print("=" * 50)
print(f"📤 Sending POST request to http://127.0.0.1:5000/ai_suggestion")
print(f"📨 Data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        'http://127.0.0.1:5000/ai_suggestion',
        json=test_data,
        headers={'Content-Type': 'application/json'},
        timeout=30
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS - AI suggestion received:")
        print(f"📝 Method: {result.get('method', 'unknown')}")
        print(f"📝 Confidence: {result.get('confidence', 'unknown')}")
        print(f"📝 Suggestion:")
        print(f"   {result.get('suggestion', 'No suggestion')}")
        print(f"\n📊 Full Response:")
        print(json.dumps(result, indent=2))
        
        # Parse the suggestion to show formatted options
        suggestion = result.get('suggestion', '')
        if 'OPTION 1:' in suggestion:
            lines = suggestion.split('\n')
            print(f"\n🎯 Parsed AI Options:")
            for line in lines:
                if line.strip().startswith(('OPTION', 'WHY:')):
                    print(f"   {line.strip()}")
    else:
        print(f"\n❌ ERROR - Status {response.status_code}")
        print(f"📝 Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error - Make sure the Flask server is running")
    print("   Run: python run.py")
except Exception as e:
    print(f"\n❌ Error: {e}")

print(f"\n🔍 This is exactly what happens when you click the AI Assistance icon:")
print(f"   1. UI detects issue: 'Avoid using ALL CAPS for emphasis...'")
print(f"   2. User clicks AI assistance icon on the sentence")
print(f"   3. JavaScript sends this exact request to /ai_suggestion")
print(f"   4. Backend processes with RAG (if available) or fallback")
print(f"   5. Response shows formatted options like OPTION 1, OPTION 2, WHY")
