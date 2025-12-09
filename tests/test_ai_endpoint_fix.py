#!/usr/bin/env python3
"""
Test the AI suggestion endpoint directly to verify the fix works in production
"""
import requests
import json
import sys

def test_ai_endpoint():
    print("🧪 Testing AI Suggestion Endpoint - Fixed Version")
    print("=" * 60)
    
    # Test cases that previously returned "(revised)"
    test_cases = [
        {
            "feedback": "Avoid using ALL CAPS for emphasis. Use bold or italics instead.",
            "sentence": "The configuration of SIMATIC S7+ Connector offers flexibility through manual configuration or file importation.",
            "document_type": "technical",
            "writing_goals": ["clarity", "conciseness"],
            "description": "ALL CAPS issue"
        },
        {
            "feedback": "Passive voice detected: 'are displayed' - convert to active voice for clearer, more direct communication.",
            "sentence": "The configuration options of the data source are displayed.",
            "document_type": "technical", 
            "writing_goals": ["clarity"],
            "description": "Passive voice issue"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"📝 Original: {test_case['sentence']}")
        print(f"⚠️  Issue: {test_case['feedback']}")
        print(f"📤 Sending POST request to http://127.0.0.1:5001/ai_suggestion")
        
        try:
            response = requests.post(
                'http://127.0.0.1:5001/ai_suggestion',
                json={
                    "feedback": test_case["feedback"],
                    "sentence": test_case["sentence"],
                    "document_type": test_case["document_type"],
                    "writing_goals": test_case["writing_goals"]
                },
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                suggestion = data.get("suggestion", "No suggestion")
                method = data.get("method", "unknown")
                confidence = data.get("confidence", "unknown")
                
                print(f"✅ Suggestion: {suggestion}")
                print(f"🔧 Method: {method}")
                print(f"📈 Confidence: {confidence}")
                
                # Check if it's the old problematic response
                if "(revised)" in suggestion.lower():
                    print("❌ FAILED: Still returning '(revised)' - fix didn't work in production!")
                elif suggestion == test_case["sentence"]:
                    print("❌ FAILED: Returning original sentence unchanged!")
                elif suggestion.strip() == "":
                    print("❌ FAILED: Empty suggestion!")
                else:
                    print("✅ SUCCESS: Meaningful suggestion generated in production!")
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ ERROR: Cannot connect to server. Make sure Flask server is running on port 5001")
            print("💡 Start server with: python run_simple.py")
            break
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete")
    print("💡 If server is not running, start it with: python run_simple.py")

if __name__ == "__main__":
    test_ai_endpoint()
