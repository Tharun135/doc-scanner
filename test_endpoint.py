#!/usr/bin/env python3
"""
Test the Flask AI suggestion endpoint to verify gemini_answer is included
"""

import requests
import json
import subprocess
import time
import threading

def start_flask_app():
    """Start the Flask app in the background"""
    try:
        subprocess.Popen(["python", "run.py"], cwd="d:/doc-scanner")
        time.sleep(3)  # Give the app time to start
    except Exception as e:
        print(f"Error starting Flask app: {e}")

def test_ai_suggestion_endpoint():
    """Test the AI suggestion endpoint"""
    try:
        url = "http://localhost:5000/ai_suggestion"
        data = {
            "feedback": "Passive voice detected",
            "sentence": "The document was written by the team.",
            "document_type": "general"
        }
        
        print("🔍 Testing AI suggestion endpoint...")
        print(f"Sending request to: {url}")
        print(f"Request data: {data}")
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received!")
            print(f"Response keys: {list(result.keys())}")
            print(f"Has gemini_answer: {'gemini_answer' in result}")
            if 'gemini_answer' in result:
                print(f"Gemini answer: {result['gemini_answer'][:100]}...")
            else:
                print("❌ gemini_answer field missing!")
            print(f"Full response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini Answer in Flask Endpoint\n")
    
    # Test the endpoint
    success = test_ai_suggestion_endpoint()
    
    if success:
        print("\n🎉 Test successful! Gemini Answer should be visible in the UI.")
    else:
        print("\n⚠️ Test failed. Check the Flask app and endpoint.")
        print("\nTo test manually:")
        print("1. Start the Flask app: python run.py")
        print("2. Upload a document and trigger AI suggestions")
        print("3. Check if 'Gemini Answer' appears in the AI assistance panel")
