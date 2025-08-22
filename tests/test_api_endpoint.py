#!/usr/bin/env python3
"""
Test the actual API endpoint to see if RAG is being used
"""

import requests
import json

def test_api_endpoint():
    """Test the API endpoint with the passive voice issue."""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    test_data = {
        "feedback": "Passive voice detected: 'are displayed' - convert to active voice for clearer, more direct communication.",
        "sentence": "The configuration options of the data source are displayed.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"]
    }
    
    print("Testing API endpoint...")
    print(f"URL: {url}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Look for the response structure
            print(f"Response structure: {list(result.keys())}")
            if 'method' in result:
                print(f"Method used: {result['method']}")
            if 'suggestion' in result:
                print(f"Suggestion: {result['suggestion']}")
            if 'confidence' in result:
                print(f"Confidence: {result['confidence']}")
            if 'ai_answer' in result:
                print(f"AI Answer: {result['ai_answer']}")
                
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")

if __name__ == "__main__":
    test_api_endpoint()
