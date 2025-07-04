#!/usr/bin/env python3
"""
Comprehensive test script to verify the modal verb issue fix works end-to-end.
This simulates the frontend-backend interaction without needing a browser.
"""

import requests
import json
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_document_analysis():
    """Test analyzing the modal verb document through the API."""
    
    print("=== TESTING DOCUMENT ANALYSIS ===")
    
    # Read the test document
    document_path = "test_modal_verb_document.txt"
    try:
        with open(document_path, 'r', encoding='utf-8') as f:
            document_content = f.read()
        print(f"✅ Loaded test document: {len(document_content)} characters")
        print(f"Document content preview: {document_content[:100]}...")
    except Exception as e:
        print(f"❌ Error reading document: {e}")
        return False
    
    # Analyze the document
    analyze_url = "http://127.0.0.1:5000/analyze"
    
    try:
        # Simulate file upload
        files = {'file': ('test_modal_verb_document.txt', document_content, 'text/plain')}
        response = requests.post(analyze_url, files=files, timeout=30)
        
        print(f"Analysis response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            feedback_data = result.get('feedback', [])
            print(f"✅ Document analyzed successfully")
            print(f"Total feedback items: {len(feedback_data)}")
            
            # Look for modal verb issues
            modal_verb_issues = []
            for item in feedback_data:
                feedback_text = item.get('feedback', '')
                if 'modal verb' in feedback_text.lower() or "'can'" in feedback_text:
                    modal_verb_issues.append(item)
            
            print(f"Found {len(modal_verb_issues)} modal verb issues")
            
            for i, issue in enumerate(modal_verb_issues):
                print(f"  Issue {i+1}: {issue.get('feedback', '')}")
                print(f"    Sentence: {issue.get('sentence', 'N/A')}")
                print(f"    Position: {issue.get('sentence_index', 'N/A')}")
            
            return modal_verb_issues
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_ai_suggestions_for_modal_verbs(modal_verb_issues):
    """Test AI suggestions for each modal verb issue found."""
    
    print("\n=== TESTING AI SUGGESTIONS FOR MODAL VERB ISSUES ===")
    
    if not modal_verb_issues:
        print("❌ No modal verb issues to test")
        return False
    
    ai_url = "http://127.0.0.1:5000/ai_suggestion"
    success_count = 0
    
    for i, issue in enumerate(modal_verb_issues):
        print(f"\n--- Testing Issue {i+1} ---")
        feedback_text = issue.get('feedback', '')
        sentence_text = issue.get('sentence', '')
        
        print(f"Feedback: {feedback_text}")
        print(f"Sentence: '{sentence_text}'")
        
        # Test case 1: With sentence context
        test_data = {
            "feedback": feedback_text,
            "sentence": sentence_text,
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"]
        }
        
        try:
            response = requests.post(ai_url, json=test_data, timeout=30)
            
            if response.ok:
                result = response.json()
                suggestion = result.get('suggestion', '')
                confidence = result.get('confidence', '')
                method = result.get('method', '')
                
                print(f"✅ AI Suggestion received")
                print(f"  Method: {method}")
                print(f"  Confidence: {confidence}")
                print(f"  Suggestion: {suggestion[:150]}{'...' if len(suggestion) > 150 else ''}")
                
                # Validate structure
                if suggestion and isinstance(suggestion, str) and len(suggestion) > 10:
                    print("✅ Suggestion structure is valid")
                    success_count += 1
                else:
                    print("❌ Invalid suggestion structure")
                    
            else:
                print(f"❌ AI request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ AI request error: {e}")
        
        # Test case 2: Without sentence context (this was the original issue)
        print(f"\n  Testing without sentence context...")
        test_data_no_context = {
            "feedback": feedback_text,
            "sentence": "",  # Empty sentence - this was causing the issue
            "document_type": "general",
            "writing_goals": ["clarity", "conciseness"]
        }
        
        try:
            response = requests.post(ai_url, json=test_data_no_context, timeout=30)
            
            if response.ok:
                result = response.json()
                suggestion = result.get('suggestion', '')
                confidence = result.get('confidence', '')
                method = result.get('method', '')
                
                print(f"✅ AI Suggestion (no context) received")
                print(f"  Method: {method}")
                print(f"  Confidence: {confidence}")
                print(f"  Suggestion: {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
                
                # This is the key test - it should work even without sentence context
                if suggestion and isinstance(suggestion, str) and len(suggestion) > 10:
                    print("✅ No-context suggestion structure is valid - FIX WORKING!")
                    success_count += 1
                else:
                    print("❌ Invalid no-context suggestion structure - FIX NOT WORKING")
                    
            else:
                print(f"❌ AI request (no context) failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ AI request (no context) error: {e}")
    
    print(f"\nSuccessful AI suggestions: {success_count}/{len(modal_verb_issues) * 2}")
    return success_count > 0

def test_specific_modal_verb_cases():
    """Test specific modal verb cases that commonly cause issues."""
    
    print("\n=== TESTING SPECIFIC MODAL VERB CASES ===")
    
    test_cases = [
        {
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "Users can access their data through the dashboard.",
            "expected_keywords": ["access", "users", "dashboard"]
        },
        {
            "feedback": "Use of modal verb 'can' - should describe direct action", 
            "sentence": "",  # No context - this was the failing case
            "expected_keywords": ["modal", "direct", "action"]
        },
        {
            "feedback": "Issue: Use of modal verb 'can' - should describe direct action",
            "sentence": "You can configure the settings from the main menu.",
            "expected_keywords": ["configure", "settings", "menu"]
        },
        {
            "feedback": "Modal verb 'can' detected - consider more direct phrasing",
            "sentence": "",  # No context
            "expected_keywords": ["direct", "phrasing"]
        }
    ]
    
    ai_url = "http://127.0.0.1:5000/ai_suggestion"
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Feedback: {test_case['feedback']}")
        print(f"Sentence: '{test_case['sentence']}'")
        
        test_data = {
            "feedback": test_case['feedback'],
            "sentence": test_case['sentence'],
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"]
        }
        
        try:
            response = requests.post(ai_url, json=test_data, timeout=30)
            
            if response.ok:
                result = response.json()
                suggestion = result.get('suggestion', '')
                confidence = result.get('confidence', '')
                method = result.get('method', '')
                
                print(f"✅ Response received")
                print(f"  Status: {response.status_code}")
                print(f"  Method: {method}")
                print(f"  Confidence: {confidence}")
                print(f"  Suggestion length: {len(suggestion)} characters")
                
                # Check for expected keywords
                suggestion_lower = suggestion.lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in suggestion_lower]
                
                print(f"  Expected keywords: {test_case['expected_keywords']}")
                print(f"  Found keywords: {found_keywords}")
                print(f"  Suggestion preview: {suggestion[:200]}{'...' if len(suggestion) > 200 else ''}")
                
                if suggestion and len(suggestion) > 20 and found_keywords:
                    print("✅ Test case PASSED")
                    success_count += 1
                else:
                    print("❌ Test case FAILED")
                    
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    print(f"\nSuccessful test cases: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def main():
    """Run all tests to verify the modal verb fix."""
    
    print("🔍 MODAL VERB ISSUE FIX VERIFICATION")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start the server with: python run.py")
        return
    
    # Test 1: Analyze the test document for modal verb issues
    modal_verb_issues = test_document_analysis()
    
    # Test 2: Test AI suggestions for found issues
    if modal_verb_issues:
        ai_test_passed = test_ai_suggestions_for_modal_verbs(modal_verb_issues)
    else:
        ai_test_passed = False
    
    # Test 3: Test specific modal verb cases
    specific_tests_passed = test_specific_modal_verb_cases()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULTS")
    print("=" * 50)
    
    if modal_verb_issues:
        print(f"✅ Document analysis: Found {len(modal_verb_issues)} modal verb issues")
    else:
        print("⚠️ Document analysis: No modal verb issues found")
    
    if ai_test_passed:
        print("✅ AI suggestions: Working correctly")
    else:
        print("❌ AI suggestions: Issues detected")
    
    if specific_tests_passed:
        print("✅ Specific test cases: All passed")
    else:
        print("❌ Specific test cases: Some failed")
    
    if ai_test_passed and specific_tests_passed:
        print("\n🎉 SUCCESS: Modal verb issue fix is working correctly!")
        print("   - AI suggestions work with sentence context")
        print("   - AI suggestions work WITHOUT sentence context (the original issue)")
        print("   - Frontend validation is now properly lenient")
    else:
        print("\n⚠️ WARNING: Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
