#!/usr/bin/env python
"""
Test the Flask app AI suggestion endpoint directly
"""
import requests
import json
import time

def test_ai_endpoint():
    """Test the Flask app AI suggestion endpoint"""
    
    # Test data from user's examples
    test_cases = [
        {
            "name": "Passive Voice Example 1",
            "feedback": "Avoid passive voice in sentence: 'The page opens displaying Databus Credentials details, and by default you will be navigated to the Data Publisher settings tab.'",
            "sentence": "The page opens displaying Databus Credentials details, and by default you will be navigated to the Data Publisher settings tab.",
            "issue_type": "Passive Voice"
        },
        {
            "name": "Passive Voice Example 2", 
            "feedback": "Avoid passive voice in sentence: 'Common Configurator is now connected Databus.'",
            "sentence": "Common Configurator is now connected Databus.",
            "issue_type": "Passive Voice"
        }
    ]
    
    base_url = "http://localhost:5000"
    endpoint = "/ai_suggestion"
    
    print("🧪 Testing Flask App AI Suggestions")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)
        
        payload = {
            "feedback": test_case["feedback"],
            "sentence": test_case["sentence"],
            "document_type": "general",
            "writing_goals": ["clarity", "conciseness"],
            "issue_type": test_case["issue_type"]
        }
        
        try:
            response = requests.post(
                base_url + endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: Success")
                print(f"   Method: {result.get('method', 'unknown')}")
                print(f"   Suggestion: {result.get('suggestion', '')[:100]}...")
                print(f"   AI Answer: {result.get('ai_answer', '')[:100]}...")
                
                # Check if using RAG or falling back
                method = result.get('method', '').lower()
                if 'rag' in method:
                    print(f"   🎉 SUCCESS: Using RAG method!")
                elif 'smart_fallback' in method:
                    print(f"   ⚠️  WARNING: Still using smart_fallback")
                else:
                    print(f"   ℹ️  INFO: Using method: {method}")
                    
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure Flask app is running on http://localhost:5000")
            print("   Start with: python app/app.py")
            return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n{'=' * 50}")
    print("🎯 Expected: method should be 'rag_rewrite' or similar RAG method")
    print("🚫 Unwanted: method should NOT be 'smart_fallback'")
    return True

if __name__ == "__main__":
    test_ai_endpoint()
