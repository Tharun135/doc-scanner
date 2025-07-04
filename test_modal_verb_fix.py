#!/usr/bin/env python3
"""
Test script to verify the modal verb issue fix by testing the endpoint directly.
"""

import requests
import json

def test_modal_verb_issue_endpoint():
    """Test the modal verb issue through the HTTP endpoint."""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    # Test case 1: Modal verb issue without sentence context (this was failing before)
    test_data_1 = {
        "feedback": "Use of modal verb 'can' - should describe direct action",
        "sentence": "",  # Empty sentence - this was causing the frontend validation to fail
        "document_type": "general",
        "writing_goals": ["clarity", "conciseness"]
    }
    
    print("=== TEST 1: Modal verb issue without sentence context ===")
    print(f"Request data: {json.dumps(test_data_1, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data_1, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.ok:
            result = response.json()
            print(f"✅ SUCCESS: Response received")
            print(f"Response keys: {list(result.keys())}")
            print(f"Suggestion: {result.get('suggestion', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Method: {result.get('method', 'N/A')}")
            
            # Validate structure
            if result.get('suggestion') and isinstance(result.get('suggestion'), str):
                print("✅ VALIDATION: Response structure is valid")
                return True
            else:
                print("❌ VALIDATION: Invalid response structure")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False

def test_modal_verb_with_context():
    """Test with sentence context for comparison."""
    
    url = "http://127.0.0.1:5000/ai_suggestion"
    
    # Test case 2: Modal verb issue with sentence context
    test_data_2 = {
        "feedback": "Use of modal verb 'can' - should describe direct action",
        "sentence": "Users can access their data through the dashboard.",
        "document_type": "technical",
        "writing_goals": ["clarity", "directness"]
    }
    
    print("\n=== TEST 2: Modal verb issue with sentence context ===")
    print(f"Request data: {json.dumps(test_data_2, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data_2, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"✅ SUCCESS: Response received")
            print(f"Suggestion: {result.get('suggestion', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Method: {result.get('method', 'N/A')}")
            
            # Validate structure
            if result.get('suggestion') and isinstance(result.get('suggestion'), str):
                print("✅ VALIDATION: Response structure is valid")
                return True
            else:
                print("❌ VALIDATION: Invalid response structure")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing modal verb issue fix...\n")
    
    # Test the specific issue that was failing
    test1_passed = test_modal_verb_issue_endpoint()
    
    # Test with context for comparison
    test2_passed = test_modal_verb_with_context()
    
    print("\n=== SUMMARY ===")
    print(f"Test 1 (no context): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (with context): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED - Modal verb issue fix is working!")
    else:
        print("\n⚠️ Some tests failed - check the output above for details")
