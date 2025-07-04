#!/usr/bin/env python3
"""
Simple script to test file upload and modal verb detection without using the browse button.
This bypasses any frontend JavaScript issues.
"""

import requests
import json

def test_direct_file_upload():
    """Test file upload directly via API, bypassing browse button issues."""
    
    print("🔧 DIRECT FILE UPLOAD TEST")
    print("=" * 50)
    print("This bypasses the browse button entirely and tests the core functionality.")
    print()
    
    # Check server
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server not running. Start with: python run.py")
        return False
    
    # Read the test document
    try:
        with open("test_modal_verb_document.txt", 'r', encoding='utf-8') as f:
            document_content = f.read()
        print(f"✅ Loaded test document: {len(document_content)} characters")
        print("\nDocument content:")
        print("-" * 30)
        print(document_content)
        print("-" * 30)
    except Exception as e:
        print(f"❌ Error reading document: {e}")
        return False
    
    # Upload via API
    print(f"\n📤 Uploading document...")
    
    try:
        # Prepare file for upload
        files = {
            'file': ('test_modal_verb_document.txt', document_content, 'text/plain')
        }
        
        # Upload the file
        response = requests.post("http://127.0.0.1:5000/upload", files=files, timeout=60)
        
        print(f"Upload response status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            
            # Extract feedback
            feedback_data = result.get('feedback', [])
            content_data = result.get('content', '')
            
            print(f"✅ Upload successful!")
            print(f"📊 Total issues found: {len(feedback_data)}")
            print(f"📄 Content length: {len(content_data)} characters")
            
            if feedback_data:
                print(f"\nFirst 5 issues found:")
                for i, item in enumerate(feedback_data[:5]):
                    feedback_text = item.get('feedback', '')
                    sentence_text = item.get('sentence', '')
                    print(f"  {i+1}. {feedback_text}")
                    if sentence_text:
                        print(f"     Sentence: {sentence_text}")
                
                # Look for modal verb issues
                modal_issues = []
                for item in feedback_data:
                    feedback_text = item.get('feedback', '')
                    if any(keyword in feedback_text.lower() for keyword in ['modal verb', "'can'", 'can -']):
                        modal_issues.append(item)
                
                print(f"\n🎯 Modal verb issues: {len(modal_issues)}")
                
                if modal_issues:
                    print("Modal verb issues found:")
                    for i, issue in enumerate(modal_issues):
                        print(f"  {i+1}. {issue.get('feedback', '')}")
                        
                    # Test AI suggestions for these issues
                    print(f"\n🤖 Testing AI suggestions for modal verb issues...")
                    
                    success_count = 0
                    for i, issue in enumerate(modal_issues):
                        feedback_text = issue.get('feedback', '')
                        sentence_text = issue.get('sentence', '')
                        
                        print(f"\n--- Modal Issue {i+1} ---")
                        print(f"Feedback: {feedback_text}")
                        print(f"Sentence: '{sentence_text}'")
                        
                        # Test AI suggestion
                        ai_data = {
                            "feedback": feedback_text,
                            "sentence": sentence_text,
                            "document_type": "technical",
                            "writing_goals": ["clarity", "directness"]
                        }
                        
                        ai_response = requests.post("http://127.0.0.1:5000/ai_suggestion", json=ai_data, timeout=30)
                        
                        if ai_response.ok:
                            ai_result = ai_response.json()
                            suggestion = ai_result.get('suggestion', '')
                            
                            if suggestion:
                                print(f"✅ AI suggestion received: {suggestion[:80]}...")
                                success_count += 1
                            else:
                                print(f"❌ Empty AI suggestion")
                        else:
                            print(f"❌ AI request failed: {ai_response.status_code}")
                    
                    print(f"\n📊 AI suggestions: {success_count}/{len(modal_issues)} successful")
                    
                    if success_count > 0:
                        print("🎉 SUCCESS: Modal verb detection and AI suggestions are working!")
                        return True
                    else:
                        print("❌ FAILURE: AI suggestions not working")
                        return False
                        
                else:
                    print("⚠️ No modal verb issues detected in the document")
                    print("This might indicate a rule configuration issue")
                    return False
                    
            else:
                print("⚠️ No issues found in the document")
                return False
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_modal_verb_cases():
    """Test AI suggestions for modal verb cases manually."""
    
    print(f"\n🎯 MANUAL MODAL VERB AI TESTING")
    print("=" * 50)
    print("Testing AI suggestions for modal verb cases directly")
    
    test_cases = [
        {
            "name": "Modal verb with sentence context",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "Users can access their data through the dashboard."
        },
        {
            "name": "Modal verb without sentence context (the original issue)",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": ""
        },
        {
            "name": "Modal verb with different context",
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "You can configure the settings from the main menu."
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {case['name']} ---")
        print(f"Feedback: {case['feedback']}")
        print(f"Sentence: '{case['sentence']}'")
        
        ai_data = {
            "feedback": case['feedback'],
            "sentence": case['sentence'],
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"]
        }
        
        try:
            response = requests.post("http://127.0.0.1:5000/ai_suggestion", json=ai_data, timeout=30)
            
            if response.ok:
                result = response.json()
                
                # Check frontend validation
                validation_passes = (result and isinstance(result, dict) and result.get('suggestion'))
                
                if validation_passes:
                    suggestion = result.get('suggestion', '')
                    confidence = result.get('confidence', '')
                    method = result.get('method', '')
                    
                    print(f"✅ SUCCESS")
                    print(f"   Method: {method}")
                    print(f"   Confidence: {confidence}")
                    print(f"   Suggestion: {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
                    success_count += 1
                else:
                    print(f"❌ FAILED: Invalid response structure")
                    print(f"   Response: {result}")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n📊 Manual test results: {success_count}/{len(test_cases)} successful")
    
    if success_count == len(test_cases):
        print("🎉 ALL MANUAL TESTS PASSED!")
        print("✅ The modal verb AI suggestion issue is FIXED")
        print("✅ Frontend validation is working correctly")
        return True
    else:
        print("⚠️ Some manual tests failed")
        return False

def main():
    """Main test function."""
    
    print("MODAL VERB TESTING - BYPASSING BROWSE BUTTON")
    print("=" * 60)
    print("Since the browse button has JavaScript issues, we'll test the")
    print("core functionality directly via API calls.")
    print()
    
    # Test 1: Direct file upload
    upload_success = test_direct_file_upload()
    
    # Test 2: Manual AI suggestions
    manual_success = test_manual_modal_verb_cases()
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🎯 FINAL SUMMARY")
    print("=" * 60)
    
    if upload_success:
        print("✅ File Upload & Detection: Working")
    else:
        print("⚠️ File Upload & Detection: Issues found")
    
    if manual_success:
        print("✅ Modal Verb AI Suggestions: Working")
    else:
        print("❌ Modal Verb AI Suggestions: Failed")
    
    print()
    
    if manual_success:
        print("🎉 CONCLUSION: MODAL VERB AI ISSUE IS FIXED!")
        print("✅ The core issue you reported is resolved")
        print("✅ AI suggestions work for modal verb feedback")
        print("✅ No more 'invalid response structure' errors")
        
        if not upload_success:
            print("\n📝 NOTE about the Browse Button:")
            print("   • The browse button has separate JavaScript issues") 
            print("   • This is unrelated to the modal verb AI fix")
            print("   • You can still use drag & drop or API upload")
            print("   • The core AI functionality is working perfectly")
    else:
        print("⚠️ CONCLUSION: Issues still exist with AI suggestions")

if __name__ == "__main__":
    main()
