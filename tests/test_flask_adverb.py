"""
Test the Flask API with the exact user example
"""
import urllib.request
import json
import time

print("🔧 Testing Flask API with user's exact adverb example...")

# Wait for server to fully start
time.sleep(5)

# User's exact example
test_data = {
    'feedback': "Check use of adverb: 'efficiently' in sentence 'The Logbook offers a detailed record of diagnostic and alarm events, helping you in tracking performance and identifying recurring issues efficiently.'",
    'sentence': "The Logbook offers a detailed record of diagnostic and alarm events, helping you in tracking performance and identifying recurring issues efficiently.",
    'document_type': 'technical',
    'option_number': 1
}

try:
    # Convert to JSON
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        'http://127.0.0.1:5000/ai_suggestion',
        data=json_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print("Making request to Flask API...")
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        
        print(f"\n✅ SUCCESS! API Response:")
        print(f"Status: {response.status}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'none')}")
        
        # Check if it's the problematic response
        suggestion = result.get('suggestion', '')
        if "Consider Revising For Better Clarity:" in suggestion and suggestion.endswith("efficiently."):
            print("\n❌ PROBLEM CONFIRMED: Still getting generic response that ends with original sentence")
            print("The web interface is not using our improved RAG system!")
        elif "Consider Revising For Better Clarity:" in suggestion:
            print("\n⚠️ PARTIAL PROBLEM: Generic response detected but content might be different")
        else:
            print(f"\n🎉 SUCCESS: Intelligent suggestion provided!")
            if "efficiently" not in suggestion:
                print("🎉 BONUS: 'efficiently' was removed/addressed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
