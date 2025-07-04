#!/usr/bin/env python3
"""
Test script to upload the modal verb document and test the AI suggestions
without needing to use the Browse button in the web interface.
"""

import requests
import json
import time

def test_file_upload_and_analysis():
    """Upload the test document and analyze it for modal verb issues."""
    
    print("🔍 TESTING FILE UPLOAD AND MODAL VERB DETECTION")
    print("=" * 60)
    
    # Read the test document
    try:
        with open("test_modal_verb_document.txt", 'r', encoding='utf-8') as f:
            document_content = f.read()
        print(f"✅ Loaded test document: {len(document_content)} characters")
        print("Document content:")
        print("-" * 40)
        print(document_content)
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error reading document: {e}")
        return False
    
    # Upload the document via API
    upload_url = "http://127.0.0.1:5000/upload"
    
    try:
        # Prepare the file upload
        files = {
            'file': ('test_modal_verb_document.txt', document_content, 'text/plain')
        }
        
        print(f"\n📤 Uploading document to {upload_url}")
        response = requests.post(upload_url, files=files, timeout=60)
        
        print(f"Upload response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print("✅ Document uploaded and analyzed successfully!")
            
            # Extract feedback data
            feedback_data = result.get('feedback', [])
            total_issues = len(feedback_data)
            print(f"📊 Total issues found: {total_issues}")
            
            # Look for modal verb issues specifically
            modal_verb_issues = []
            for item in feedback_data:
                feedback_text = item.get('feedback', '')
                if any(keyword in feedback_text.lower() for keyword in ['modal verb', "'can'", "can -"]):
                    modal_verb_issues.append(item)
            
            print(f"🎯 Modal verb issues found: {len(modal_verb_issues)}")
            
            if modal_verb_issues:
                print("\nModal verb issues detected:")
                for i, issue in enumerate(modal_verb_issues):
                    print(f"  {i+1}. {issue.get('feedback', '')}")
                    print(f"     Sentence: {issue.get('sentence', 'N/A')}")
                    print(f"     Position: {issue.get('sentence_index', 'N/A')}")
                
                return modal_verb_issues
            else:
                print("⚠️ No modal verb issues found in the document")
                print("Let's check what issues were found:")
                for i, item in enumerate(feedback_data[:5]):  # Show first 5 issues
                    print(f"  {i+1}. {item.get('feedback', '')}")
                return []
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_modal_verb_ai_suggestions(modal_verb_issues):
    """Test AI suggestions for the found modal verb issues."""
    
    if not modal_verb_issues:
        print("\n⚠️ No modal verb issues to test AI suggestions for")
        return False
    
    print(f"\n🤖 TESTING AI SUGGESTIONS FOR {len(modal_verb_issues)} MODAL VERB ISSUES")
    print("=" * 60)
    
    ai_url = "http://127.0.0.1:5000/ai_suggestion"
    success_count = 0
    
    for i, issue in enumerate(modal_verb_issues):
        print(f"\n--- Modal Verb Issue {i+1} ---")
        feedback_text = issue.get('feedback', '')
        sentence_text = issue.get('sentence', '')
        sentence_index = issue.get('sentence_index', 'unknown')
        
        print(f"Issue: {feedback_text}")
        print(f"Sentence: '{sentence_text}'")
        print(f"Position: {sentence_index}")
        
        # Test the exact scenario that was failing before the fix
        test_data = {
            "feedback": feedback_text,
            "sentence": sentence_text,  # This might be empty, which was causing the issue
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"]
        }
        
        print(f"Sending request to AI...")
        try:
            response = requests.post(ai_url, json=test_data, timeout=30)
            
            if response.ok:
                result = response.json()
                suggestion = result.get('suggestion', '')
                confidence = result.get('confidence', '')
                method = result.get('method', '')
                
                print(f"✅ AI Response received!")
                print(f"  Method: {method}")
                print(f"  Confidence: {confidence}")
                print(f"  Suggestion length: {len(suggestion)} characters")
                
                # Show suggestion preview
                if suggestion:
                    print(f"  Suggestion preview:")
                    print(f"  {suggestion[:150]}{'...' if len(suggestion) > 150 else ''}")
                    success_count += 1
                else:
                    print(f"  ❌ Empty suggestion received")
                    
            else:
                print(f"❌ AI request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ AI request error: {e}")
    
    print(f"\n📊 AI Suggestion Results: {success_count}/{len(modal_verb_issues)} successful")
    return success_count > 0

def test_specific_problematic_case():
    """Test the specific case that was causing issues."""
    
    print(f"\n🎯 TESTING THE SPECIFIC PROBLEMATIC CASE")
    print("=" * 60)
    print("This simulates clicking on a modal verb issue in the web interface")
    
    # This is the exact type of request that was failing
    test_cases = [
        {
            "name": "Modal verb issue with sentence",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "Users can access their data through the dashboard."
        },
        {
            "name": "Modal verb issue without sentence (the problematic case)",
            "feedback": "Use of modal verb 'can' - should describe direct action", 
            "sentence": ""  # This was causing the frontend validation to fail
        },
        {
            "name": "Modal verb with 'Issue:' prefix",
            "feedback": "Issue: Use of modal verb 'can' - should describe direct action",
            "sentence": "You can configure the settings from the main menu."
        }
    ]
    
    ai_url = "http://127.0.0.1:5000/ai_suggestion"
    success_count = 0
    
    for i, case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {case['name']} ---")
        print(f"Feedback: {case['feedback']}")
        print(f"Sentence: '{case['sentence']}'")
        
        test_data = {
            "feedback": case['feedback'],
            "sentence": case['sentence'],
            "document_type": "general",
            "writing_goals": ["clarity", "conciseness"]
        }
        
        try:
            response = requests.post(ai_url, json=test_data, timeout=30)
            
            if response.ok:
                result = response.json()
                
                # Check the exact validation that the frontend does
                frontend_validation_passes = (
                    result and 
                    isinstance(result, dict) and 
                    result.get('suggestion')
                )
                
                print(f"✅ HTTP Status: {response.status_code}")
                print(f"✅ Response is dict: {isinstance(result, dict)}")
                print(f"✅ Has suggestion key: {'suggestion' in result}")
                print(f"✅ Suggestion is truthy: {bool(result.get('suggestion'))}")
                print(f"✅ Frontend validation passes: {frontend_validation_passes}")
                
                if frontend_validation_passes:
                    suggestion = result['suggestion']
                    print(f"✅ SUCCESS - No 'invalid response structure' error!")
                    print(f"   Suggestion: {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
                    success_count += 1
                else:
                    print(f"❌ Frontend validation would fail - 'invalid response structure' error")
                    print(f"   Result: {result}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
    
    print(f"\n📊 Problematic Case Results: {success_count}/{len(test_cases)} successful")
    
    if success_count == len(test_cases):
        print("🎉 ALL CASES PASSED - The original issue is FIXED!")
    else:
        print("⚠️ Some cases failed - the issue may still exist")
    
    return success_count == len(test_cases)

def main():
    """Main test function."""
    
    print("MODAL VERB ISSUE - COMPLETE TESTING WITHOUT BROWSER")
    print("=" * 60)
    print("This simulates the entire workflow without using the Browse button")
    print()
    
    # Check server
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start with: python run.py")
        return
    
    # Step 1: Upload and analyze document
    modal_verb_issues = test_file_upload_and_analysis()
    
    # Step 2: Test AI suggestions for found issues
    if modal_verb_issues:
        ai_success = test_modal_verb_ai_suggestions(modal_verb_issues)
    else:
        ai_success = False
    
    # Step 3: Test the specific problematic case
    specific_case_success = test_specific_problematic_case()
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if modal_verb_issues:
        print(f"✅ Document Analysis: Found {len(modal_verb_issues)} modal verb issues")
    else:
        print("⚠️ Document Analysis: No modal verb issues found")
    
    if ai_success:
        print("✅ AI Suggestions: Working for document issues")
    else:
        print("❌ AI Suggestions: Failed for document issues")
    
    if specific_case_success:
        print("✅ Problematic Cases: All fixed")
    else:
        print("❌ Problematic Cases: Still failing")
    
    print()
    
    if specific_case_success:
        print("🎉 CONCLUSION: The modal verb issue is FIXED!")
        print("   • No more 'invalid response structure' errors")
        print("   • AI suggestions work with and without sentence context")
        print("   • The Browse button issue is separate from the AI suggestion fix")
    else:
        print("⚠️ CONCLUSION: Issues still exist - check output above")

if __name__ == "__main__":
    main()
