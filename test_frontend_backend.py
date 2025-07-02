#!/usr/bin/env python3
"""
Frontend-Backend Integration Test for AI Suggestions
Tests the complete flow from frontend to backend
"""

import sys
import os
import requests
import json

def test_ai_suggestion_endpoint():
    """Test the AI suggestion endpoint with various scenarios"""
    
    base_url = "http://127.0.0.1:5000"
    endpoint = f"{base_url}/ai_suggestion"
    
    test_cases = [
        {
            "name": "Passive Voice Test",
            "data": {
                "feedback": "This sentence contains passive voice",
                "sentence": "The document was created by the team.",
                "document_type": "technical",
                "writing_goals": ["clarity", "active_voice"]
            }
        },
        {
            "name": "Long Sentence Test",
            "data": {
                "feedback": "This sentence is too long and complex",
                "sentence": "The comprehensive document that was meticulously prepared by the dedicated team of experts contains detailed information about the complex software implementation process.",
                "document_type": "technical",
                "writing_goals": ["clarity", "conciseness"]
            }
        },
        {
            "name": "Minimal Data Test",
            "data": {
                "feedback": "Grammar issue",
                "sentence": "This are incorrect.",
                "document_type": "general"
            }
        },
        {
            "name": "Empty Writing Goals Test",
            "data": {
                "feedback": "Word choice issue",
                "sentence": "Utilize this methodology.",
                "document_type": "technical",
                "writing_goals": []
            }
        }
    ]
    
    print("🧪 Testing AI Suggestion Endpoint")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers, json=test_case['data'], timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Suggestion: {result['suggestion'][:100]}...")
                print(f"   Confidence: {result['confidence']}")
                print(f"   Method: {result['method']}")
                if 'context_used' in result and 'model_used' in result['context_used']:
                    print(f"   Model Used: {result['context_used']['model_used']}")
            else:
                print(f"   ❌ Failed!")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)

def test_missing_parameters():
    """Test error handling for missing parameters"""
    
    base_url = "http://127.0.0.1:5000"
    endpoint = f"{base_url}/ai_suggestion"
    
    error_test_cases = [
        {
            "name": "Missing Feedback",
            "data": {
                "sentence": "The document was created by the team.",
                "document_type": "technical"
            }
        },
        {
            "name": "Missing Sentence",
            "data": {
                "feedback": "This sentence contains passive voice",
                "document_type": "technical"
            }
        },
        {
            "name": "Empty Feedback",
            "data": {
                "feedback": "",
                "sentence": "The document was created by the team.",
                "document_type": "technical"
            }
        }
    ]
    
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    for i, test_case in enumerate(error_test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(endpoint, headers=headers, json=test_case['data'], timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def check_server_health():
    """Check if the server is running and healthy"""
    
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

def main():
    print("🔍 Frontend-Backend Integration Test")
    print("=" * 60)
    
    # Check server health first
    if not check_server_health():
        print("\n❌ Server is not running. Please start the application first.")
        print("Run: python run.py")
        return
    
    # Test normal AI suggestion scenarios
    test_ai_suggestion_endpoint()
    
    # Test error handling
    test_missing_parameters()
    
    print("\n✅ Integration tests completed!")
    print("\nIf all tests passed, the AI suggestion system is working correctly.")
    print("If you're still seeing 'AI suggestion not available' in the web interface,")
    print("please check the browser console for JavaScript errors.")

if __name__ == "__main__":
    main()
