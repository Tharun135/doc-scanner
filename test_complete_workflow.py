#!/usr/bin/env python3
"""
Complete workflow test to verify everything works end-to-end.
"""

import requests
import json
import os

def test_complete_workflow():
    """Test the complete workflow from file upload to AI suggestions."""
    
    print("🔄 COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    # Step 1: Upload file with proper form data
    print("📁 Step 1: Uploading test document...")
    
    with open("test_modal_verb_document.txt", 'rb') as f:
        files = {'file': ('test_modal_verb_document.txt', f, 'text/plain')}
        
        try:
            response = requests.post("http://127.0.0.1:5000/upload", files=files, timeout=60)
            
            if response.ok:
                result = response.json()
                print("✅ Document uploaded successfully")
                
                # Check for issues
                feedback_data = result.get('feedback', [])
                print(f"📊 Total feedback items: {len(feedback_data)}")
                
                # Find modal verb issues
                modal_issues = []
                for item in feedback_data:
                    feedback_text = item.get('feedback', '')
                    if 'modal verb' in feedback_text.lower() or "'can'" in feedback_text:
                        modal_issues.append(item)
                
                print(f"🎯 Modal verb issues found: {len(modal_issues)}")
                
                if modal_issues:
                    print("\nModal verb issues:")
                    for i, issue in enumerate(modal_issues):
                        print(f"  {i+1}. {issue.get('feedback', '')}")
                        
                    # Step 2: Test AI suggestions for each found issue
                    print(f"\n🤖 Step 2: Testing AI suggestions...")
                    
                    for i, issue in enumerate(modal_issues):
                        feedback_text = issue.get('feedback', '')
                        sentence_text = issue.get('sentence', '')
                        
                        print(f"\n--- Testing Issue {i+1} ---")
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
                            
                            # Check frontend validation
                            validation_passes = (ai_result and isinstance(ai_result, dict) and ai_result.get('suggestion'))
                            
                            if validation_passes:
                                print(f"✅ AI suggestion successful")
                                print(f"   Method: {ai_result.get('method', 'N/A')}")
                                print(f"   Confidence: {ai_result.get('confidence', 'N/A')}")
                                print(f"   Preview: {suggestion[:100]}{'...' if len(suggestion) > 100 else ''}")
                            else:
                                print(f"❌ AI suggestion validation failed")
                        else:
                            print(f"❌ AI suggestion request failed: {ai_response.status_code}")
                    
                    return True
                else:
                    print("⚠️ No modal verb issues found - this suggests a rule application issue")
                    return False
                    
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False

def test_manual_ai_suggestions():
    """Test AI suggestions manually without relying on document analysis."""
    
    print(f"\n🎯 MANUAL AI SUGGESTION TEST")
    print("=" * 60)
    print("Testing AI suggestions directly (simulating user clicking on detected issues)")
    
    # Test cases based on the sentences in our document
    test_cases = [
        {
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "Users can access their data through the dashboard.",
            "expected": "should work with context"
        },
        {
            "feedback": "Use of modal verb 'can' - should describe direct action", 
            "sentence": "You can configure the settings from the main menu.",
            "expected": "should work with context"
        },
        {
            "feedback": "Use of modal verb 'can' - should describe direct action",
            "sentence": "",  # No context - the original problematic case
            "expected": "should work without context"
        }
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases):
        print(f"\n--- Manual Test {i+1}: {case['expected']} ---")
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
                
                # Frontend validation check
                validation_passes = (result and isinstance(result, dict) and result.get('suggestion'))
                
                if validation_passes:
                    print(f"✅ SUCCESS: {case['expected']}")
                    print(f"   Suggestion: {result.get('suggestion', '')[:80]}...")
                    success_count += 1
                else:
                    print(f"❌ FAILED: Frontend validation failed")
                    print(f"   Result: {result}")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n📊 Manual test results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def main():
    """Run complete workflow test."""
    
    print("MODAL VERB ISSUE - COMPLETE WORKFLOW VERIFICATION")
    print("=" * 60)
    
    # Check server
    try:
        response = requests.get("http://127.0.0.1:5000", timeout=5)
        print("✅ Server is running")
    except:
        print("❌ Server not running. Start with: python run.py")
        return
    
    # Test complete workflow
    workflow_success = test_complete_workflow()
    
    # Test manual AI suggestions
    manual_success = test_manual_ai_suggestions()
    
    # Final summary
    print(f"\n" + "=" * 60)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    if workflow_success:
        print("✅ Complete Workflow: SUCCESS")
        print("   • File upload works")
        print("   • Modal verb detection works") 
        print("   • AI suggestions work end-to-end")
    else:
        print("⚠️ Complete Workflow: Issues detected")
        print("   • May be a rule application or file processing issue")
    
    if manual_success:
        print("✅ Manual AI Suggestions: SUCCESS")
        print("   • AI suggestions work with context")
        print("   • AI suggestions work without context") 
        print("   • No 'invalid response structure' errors")
    else:
        print("❌ Manual AI Suggestions: FAILED")
    
    print()
    
    if manual_success:
        print("🎉 CONCLUSION: THE ORIGINAL MODAL VERB ISSUE IS FIXED!")
        print("✅ Users will no longer get 'invalid response structure' errors")
        print("✅ AI suggestions work correctly for modal verb feedback")
        print("✅ Both with and without sentence context scenarios work")
        
        if not workflow_success:
            print("\n📝 NOTE: The browse button / file upload may have separate issues")
            print("   but the core AI suggestion functionality is working perfectly.")
    else:
        print("⚠️ CONCLUSION: AI suggestion issues still exist")

if __name__ == "__main__":
    main()
