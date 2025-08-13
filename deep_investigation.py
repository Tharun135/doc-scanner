#!/usr/bin/env python3
"""
Deep Investigation: Full Pipeline Debug
Trace every step from backend to frontend to find exactly where issues are lost
"""

import requests
import json
import time
import sys
sys.path.append('app')

def deep_investigate():
    """Deep investigation of the entire pipeline"""
    
    print("🔍 DEEP INVESTIGATION: FULL PIPELINE DEBUG")
    print("=" * 80)
    
    # Wait for server
    time.sleep(3)
    
    # Test content that should trigger multiple rules
    test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
    
    print(f"Test content: {test_content[:100]}...")
    print("=" * 80)
    
    # STEP 1: Test backend directly
    print("STEP 1: TESTING BACKEND DIRECTLY")
    print("-" * 40)
    
    try:
        from app.app import get_rules, review_document
        
        rules = get_rules()
        backend_result = review_document(test_content, rules)
        backend_issues = backend_result.get('issues', [])
        
        print(f"Backend detected {len(backend_issues)} issues:")
        backend_types = {}
        for i, issue in enumerate(backend_issues[:10]):  # Show first 10
            message = issue.get('message', 'No message')
            print(f"  {i+1}. {message[:60]}...")
            
            # Categorize
            if 'passive voice' in message.lower():
                backend_types['passive_voice'] = backend_types.get('passive_voice', 0) + 1
            elif 'long sentence' in message.lower():
                backend_types['long_sentence'] = backend_types.get('long_sentence', 0) + 1
            elif 'modifier' in message.lower():
                backend_types['modifier'] = backend_types.get('modifier', 0) + 1
            else:
                backend_types['other'] = backend_types.get('other', 0) + 1
        
        print(f"Backend issue types: {backend_types}")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        backend_issues = []
        backend_types = {}
    
    # STEP 2: Test Flask upload endpoint
    print(f"\nSTEP 2: TESTING FLASK UPLOAD ENDPOINT")
    print("-" * 40)
    
    # Create test file
    test_file = 'deep_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        url = 'http://127.0.0.1:5000/upload'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                flask_result = response.json()
                
                # Save full response
                with open('deep_investigation_response.json', 'w', encoding='utf-8') as f:
                    json.dump(flask_result, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Flask response saved to 'deep_investigation_response.json'")
                
                if 'sentences' in flask_result:
                    sentences = flask_result['sentences']
                    print(f"Flask returned {len(sentences)} sentences")
                    
                    total_flask_issues = 0
                    flask_types = {}
                    
                    for i, sentence in enumerate(sentences):
                        feedback = sentence.get('feedback', [])
                        sentence_text = sentence.get('sentence', '')
                        
                        print(f"\nSentence {i+1}: '{sentence_text[:50]}...'")
                        print(f"  Issues in this sentence: {len(feedback)}")
                        
                        if feedback:
                            for j, issue in enumerate(feedback[:3]):  # Show first 3
                                if isinstance(issue, dict):
                                    message = issue.get('message', 'No message')
                                    print(f"    {j+1}. {message[:60]}...")
                                    
                                    # Categorize
                                    if 'passive voice' in message.lower():
                                        flask_types['passive_voice'] = flask_types.get('passive_voice', 0) + 1
                                    elif 'long sentence' in message.lower():
                                        flask_types['long_sentence'] = flask_types.get('long_sentence', 0) + 1
                                    elif 'modifier' in message.lower():
                                        flask_types['modifier'] = flask_types.get('modifier', 0) + 1
                                    else:
                                        flask_types['other'] = flask_types.get('other', 0) + 1
                        
                        total_flask_issues += len(feedback)
                    
                    print(f"\nFlask total issues: {total_flask_issues}")
                    print(f"Flask issue types: {flask_types}")
                    
                    # STEP 3: Compare backend vs Flask
                    print(f"\nSTEP 3: BACKEND VS FLASK COMPARISON")
                    print("-" * 40)
                    
                    print(f"Backend issues: {len(backend_issues)}")
                    print(f"Flask issues: {total_flask_issues}")
                    print(f"Backend types: {backend_types}")
                    print(f"Flask types: {flask_types}")
                    
                    if len(backend_issues) > total_flask_issues:
                        print(f"❌ ISSUE LOSS: {len(backend_issues) - total_flask_issues} issues lost in Flask processing")
                    elif len(backend_issues) == total_flask_issues:
                        print(f"✅ ISSUE PRESERVATION: All backend issues preserved in Flask")
                    else:
                        print(f"⚠️  ISSUE MULTIPLICATION: Flask has more issues than backend")
                    
                    # Check if only passive voice is making it through
                    if len(flask_types) == 1 and 'passive_voice' in flask_types:
                        print(f"\n❌ CONFIRMED PROBLEM: Only passive voice issues in Flask response")
                        print(f"   Other issue types ({len(backend_types) - flask_types.get('passive_voice', 0)}) are being filtered out")
                        
                        # Let's investigate the Flask code
                        investigate_flask_filtering(sentences, backend_issues)
                    elif len(flask_types) > 1:
                        print(f"\n✅ FLASK WORKING: Multiple issue types in Flask response")
                        print(f"   Problem might be in frontend JavaScript")
                        investigate_frontend_issues()
                    else:
                        print(f"\n❓ UNEXPECTED: Flask response pattern unexpected")
                
                else:
                    print(f"❌ No 'sentences' in Flask response")
                    print(f"Response keys: {list(flask_result.keys())}")
                    
            else:
                print(f"❌ Flask request failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

def investigate_flask_filtering(sentences, backend_issues):
    """Investigate why Flask is filtering out non-passive voice issues"""
    
    print(f"\n🔧 INVESTIGATING FLASK FILTERING")
    print("-" * 40)
    
    print(f"Backend detected {len(backend_issues)} issues")
    
    # Analyze what types of issues the backend found
    backend_analysis = {}
    for issue in backend_issues:
        message = issue.get('message', '').lower()
        if 'passive voice' in message:
            backend_analysis['passive_voice'] = backend_analysis.get('passive_voice', 0) + 1
        elif 'long sentence' in message:
            backend_analysis['long_sentence'] = backend_analysis.get('long_sentence', 0) + 1
        elif 'modifier' in message:
            backend_analysis['modifier'] = backend_analysis.get('modifier', 0) + 1
        elif 'weak verb' in message:
            backend_analysis['weak_verb'] = backend_analysis.get('weak_verb', 0) + 1
        else:
            backend_analysis['other'] = backend_analysis.get('other', 0) + 1
    
    print(f"Backend issue breakdown: {backend_analysis}")
    
    # Check what made it through to Flask sentences
    flask_analysis = {}
    for sentence in sentences:
        for issue in sentence.get('feedback', []):
            message = issue.get('message', '').lower()
            if 'passive voice' in message:
                flask_analysis['passive_voice'] = flask_analysis.get('passive_voice', 0) + 1
            elif 'long sentence' in message:
                flask_analysis['long_sentence'] = flask_analysis.get('long_sentence', 0) + 1
            elif 'modifier' in message:
                flask_analysis['modifier'] = flask_analysis.get('modifier', 0) + 1
            elif 'weak verb' in message:
                flask_analysis['weak_verb'] = flask_analysis.get('weak_verb', 0) + 1
            else:
                flask_analysis['other'] = flask_analysis.get('other', 0) + 1
    
    print(f"Flask issue breakdown: {flask_analysis}")
    
    # Identify what was filtered out
    for issue_type, backend_count in backend_analysis.items():
        flask_count = flask_analysis.get(issue_type, 0)
        if flask_count < backend_count:
            print(f"❌ FILTERED OUT: {issue_type} - {backend_count - flask_count} issues lost")
    
    if len(flask_analysis) == 1 and 'passive_voice' in flask_analysis:
        print(f"\n💡 DIAGNOSIS: Flask distribution logic is only preserving passive voice issues")
        print(f"   Need to check the distribution algorithm in app.py upload route")

def investigate_frontend_issues():
    """Investigate potential frontend JavaScript issues"""
    
    print(f"\n🔧 INVESTIGATING FRONTEND ISSUES")
    print("-" * 40)
    print(f"If Flask is returning multiple issue types but you only see passive voice:")
    print(f"1. Check browser developer console (F12) for JavaScript errors")
    print(f"2. Check if frontend is filtering issues by type")
    print(f"3. Check if CSS is hiding certain issue types")
    print(f"4. Verify the JavaScript feedback rendering logic")

if __name__ == "__main__":
    deep_investigate()
