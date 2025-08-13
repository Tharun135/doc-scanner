#!/usr/bin/env python3
"""
Comprehensive Web Interface Debug Script
This script will help diagnose why the user isn't seeing issues in the web interface
"""

import requests
import json
import os

def test_web_interface():
    """Test the web interface with debugging"""
    
    # Test content that should trigger multiple rules
    test_content = """This document contains many writing issues that should be detected. The passive voice was used extensively throughout this document. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it difficult for readers to follow the main point. Additionally, the document utilizes verbose language patterns that could be simplified. Furthermore, complex terminology was implemented to demonstrate detection capabilities."""
    
    # Save test content to file
    test_file = 'web_debug_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("🔍 DEBUG: Testing web interface...")
    print(f"Test content length: {len(test_content)} characters")
    print(f"Test file created: {test_file}")
    
    # Test the upload endpoint
    url = 'http://127.0.0.1:5000/upload'
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            print(f"\n📤 Sending POST request to: {url}")
            print(f"Files: {list(files.keys())}")
            print(f"Data: {data}")
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            print(f"\n📥 Response received:")
            print(f"Status code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ SUCCESS - JSON response structure:")
                print(f"Keys in response: {list(result.keys())}")
                
                # Check sentences
                if 'sentences' in result:
                    sentences = result['sentences']
                    print(f"Number of sentences: {len(sentences)}")
                    
                    total_issues = 0
                    for i, sentence in enumerate(sentences):
                        print(f"\nSentence {i+1}:")
                        print(f"  Text: {sentence.get('sentence', 'NO SENTENCE')[:100]}...")
                        print(f"  Has feedback: {'feedback' in sentence}")
                        
                        if 'feedback' in sentence and sentence['feedback']:
                            feedback = sentence['feedback']
                            print(f"  Feedback count: {len(feedback)}")
                            total_issues += len(feedback)
                            
                            for j, issue in enumerate(feedback):
                                if isinstance(issue, dict):
                                    print(f"    Issue {j+1}: {issue.get('message', 'NO MESSAGE')}")
                                    if 'full_suggestion' in issue:
                                        print(f"    Suggestion: {issue['full_suggestion'][:100]}...")
                                else:
                                    print(f"    Issue {j+1}: {issue}")
                        else:
                            print(f"  No feedback/issues found")
                    
                    print(f"\n📊 SUMMARY:")
                    print(f"Total sentences processed: {len(sentences)}")
                    print(f"Total issues found: {total_issues}")
                    
                    if total_issues == 0:
                        print("❌ PROBLEM: No issues detected - backend may not be working correctly")
                        
                        # Let's debug the backend directly
                        print("\n🔧 Testing backend directly...")
                        test_backend_directly(test_content)
                    else:
                        print("✅ Backend is working correctly")
                        print("\n💡 If you're not seeing issues in the browser:")
                        print("1. Clear your browser cache (Ctrl+Shift+Delete)")
                        print("2. Try a hard refresh (Ctrl+F5)")
                        print("3. Check browser developer console (F12) for JavaScript errors")
                        print("4. Make sure you're uploading a .txt file")
                        print("5. Try uploading this test file: web_debug_test.txt")
                else:
                    print("❌ PROBLEM: No 'sentences' key in response")
                    print(f"Response content: {json.dumps(result, indent=2)[:500]}...")
                    
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server")
        print("Make sure the server is running: python run.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

def test_backend_directly(content):
    """Test the backend processing directly"""
    try:
        # Import the backend functions
        import sys
        sys.path.append('app')
        
        from ai_improvement import review_document
        from app import get_rules
        
        print("\n🔧 Testing backend directly...")
        
        # Get rules
        rules = get_rules()
        print(f"Rules loaded: {len(rules)}")
        
        # Test review_document function
        result = review_document(content, rules, 'technical')
        print(f"Direct backend result type: {type(result)}")
        
        if isinstance(result, list):
            print(f"Backend returned {len(result)} issues:")
            for i, issue in enumerate(result[:5]):  # Show first 5
                print(f"  {i+1}. {issue}")
        elif isinstance(result, dict):
            print(f"Backend returned dict with keys: {list(result.keys())}")
        else:
            print(f"Backend returned: {result}")
            
    except Exception as e:
        print(f"❌ Backend test error: {str(e)}")

if __name__ == "__main__":
    test_web_interface()
