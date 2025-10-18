#!/usr/bin/env python3
"""
Test to reproduce the original 'No test named match' error by making actual requests
"""
import requests
import json
import time

def test_intelligent_analysis_endpoint():
    """Test the actual intelligent analysis endpoint"""
    
    # Test data that might trigger the error
    test_cases = [
        {
            "text": "This is a simple sentence.",
            "context": "testing context"
        },
        {
            "text": "The document contains passive voice that should be improved.",
            "context": "grammar check"
        },
        {
            "text": "There are many issues with this text that need to be fixed.",
            "context": "comprehensive analysis"
        }
    ]
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔧 Testing intelligent analysis endpoint for 'No test named match' error")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['text'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/analyze_intelligent",
                json=test_case,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success', False)}")
                if result.get('error'):
                    print(f"⚠️ Error in response: {result['error']}")
                    if "No test named" in str(result['error']):
                        print("🎯 FOUND IT! The 'No test named match' error!")
                        print(f"Full error: {result['error']}")
                else:
                    print(f"📋 Result keys: {list(result.keys())}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                    if "No test named" in str(error_data):
                        print("🎯 FOUND IT! The 'No test named match' error in HTTP error!")
                except:
                    print(f"Error text: {response.text}")
                    if "No test named" in response.text:
                        print("🎯 FOUND IT! The 'No test named match' error in response text!")
                        
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused - Flask app not running")
            print("Please start the Flask app first with: python run.py")
            break
        except Exception as e:
            print(f"❌ Request error: {e}")
            if "No test named" in str(e):
                print("🎯 FOUND IT! The 'No test named match' error in request!")
    
    print("\n" + "=" * 70)
    print("🏁 Test completed")

def main():
    print("🔧 Attempting to reproduce 'No test named match' error via HTTP requests")
    test_intelligent_analysis_endpoint()

if __name__ == "__main__":
    main()