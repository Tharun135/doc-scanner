"""
Simple inline test that doesn't require external libraries
"""
import urllib.request
import urllib.parse
import json

print("Testing Flask server with basic urllib...")

data = {
    'feedback': 'Avoid passive voice in sentence',
    'sentence': 'Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.',
    'document_type': 'technical',
    'option_number': 1
}

try:
    # Convert to JSON
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        'http://127.0.0.1:5001/ai_suggestion',
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("Sending request...")
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"✅ SUCCESS!")
        print(f"Status: {response.status}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'none')}")
        
        # Check the result
        suggestion = result.get('suggestion', '')
        method = result.get('method', '')
        
        if method in ['local_rag', 'direct_rag'] and 'Consider revising:' not in suggestion:
            print("✅ 🎉 RAG IS WORKING WITH INTELLIGENT SUGGESTIONS!")
        elif method in ['local_rag', 'direct_rag']:
            print("🔄 RAG method detected but still generic suggestion")
        else:
            print(f"ℹ️ Using fallback method: {method}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
