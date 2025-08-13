#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE INVESTIGATION
Trace every single step from backend to frontend to find where issues are lost
"""

import requests
import json
import time
import sys
sys.path.append('app')

def final_investigation():
    """Final comprehensive investigation"""
    
    print("🔍 FINAL COMPREHENSIVE INVESTIGATION")
    print("=" * 80)
    
    # Wait for server
    time.sleep(3)
    
    # Test content with multiple rule triggers
    test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
    
    print(f"Test content: {test_content[:100]}...")
    print("=" * 80)
    
    # STEP 1: Test backend directly first
    print("STEP 1: BACKEND DIRECT TEST")
    print("-" * 40)
    
    try:
        from app.app import get_rules, review_document
        
        rules = get_rules()
        backend_result = review_document(test_content, rules)
        backend_issues = backend_result.get('issues', [])
        
        print(f"✅ Backend directly detected {len(backend_issues)} issues")
        
        backend_types = {}
        for issue in backend_issues:
            message = issue.get('message', '').lower()
            if 'passive voice' in message:
                backend_types['passive_voice'] = backend_types.get('passive_voice', 0) + 1
            elif 'long sentence' in message:
                backend_types['long_sentence'] = backend_types.get('long_sentence', 0) + 1
            elif 'modifier' in message:
                backend_types['modifier'] = backend_types.get('modifier', 0) + 1
            else:
                backend_types['other'] = backend_types.get('other', 0) + 1
        
        print(f"Backend issue types: {backend_types}")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return
    
    # STEP 2: Test ALL Flask upload endpoints
    print(f"\nSTEP 2: TESTING ALL FLASK ENDPOINTS")
    print("-" * 40)
    
    # Create test file
    test_file = 'final_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    endpoints_to_test = [
        '/upload',
        '/upload_progressive',
        '/upload_batch'
    ]
    
    endpoint_results = {}
    
    for endpoint in endpoints_to_test:
        print(f"\n📤 Testing {endpoint}...")
        
        try:
            url = f'http://127.0.0.1:5000{endpoint}'
            
            with open(test_file, 'rb') as f:
                files = {'file': (test_file, f, 'text/plain')}
                data = {'documentType': 'technical'}
                
                response = requests.post(url, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Save each endpoint response
                    with open(f'response_{endpoint.replace("/", "")}.json', 'w', encoding='utf-8') as rf:
                        json.dump(result, rf, indent=2, ensure_ascii=False)
                    
                    print(f"✅ {endpoint} responded successfully")
                    print(f"Response keys: {list(result.keys())}")
                    
                    # Check if it has sentences directly
                    if 'sentences' in result:
                        sentences = result['sentences']
                        total_issues = sum(len(s.get('feedback', [])) for s in sentences)
                        print(f"  Direct sentences: {len(sentences)}, Total issues: {total_issues}")
                        endpoint_results[endpoint] = {'type': 'direct', 'sentences': len(sentences), 'issues': total_issues}
                    
                    # Check if it's a progressive response with analysis_id
                    elif 'analysis_id' in result:
                        analysis_id = result['analysis_id']
                        print(f"  Progressive response with analysis_id: {analysis_id}")
                        
                        # Try to get the progress/results
                        progress_url = f'http://127.0.0.1:5000/analysis_progress/{analysis_id}'
                        
                        # Wait and check progress multiple times
                        for attempt in range(10):
                            time.sleep(2)
                            progress_response = requests.get(progress_url)
                            
                            if progress_response.status_code == 200:
                                progress_data = progress_response.json()
                                
                                print(f"    Attempt {attempt+1}: Stage={progress_data.get('stage')}, "
                                      f"Percentage={progress_data.get('percentage')}%, "
                                      f"Completed={progress_data.get('completed')}")
                                
                                if progress_data.get('completed') or progress_data.get('stage') == 'complete':
                                    # Check if result is available
                                    if 'result' in progress_data and progress_data['result']:
                                        result_data = progress_data['result']
                                        if 'sentences' in result_data:
                                            sentences = result_data['sentences']
                                            total_issues = sum(len(s.get('feedback', [])) for s in sentences)
                                            print(f"  ✅ Progressive completed: {len(sentences)} sentences, {total_issues} issues")
                                            endpoint_results[endpoint] = {'type': 'progressive', 'sentences': len(sentences), 'issues': total_issues}
                                            
                                            # Save the final result
                                            with open(f'final_result_{endpoint.replace("/", "")}.json', 'w', encoding='utf-8') as rf:
                                                json.dump(result_data, rf, indent=2, ensure_ascii=False)
                                        break
                                    else:
                                        print(f"    No result data yet...")
                        else:
                            print(f"  ❌ Progressive analysis never completed")
                            endpoint_results[endpoint] = {'type': 'progressive', 'status': 'timeout'}
                    
                    else:
                        print(f"  ❓ Unknown response format")
                        endpoint_results[endpoint] = {'type': 'unknown', 'keys': list(result.keys())}
                
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
                    endpoint_results[endpoint] = {'type': 'error', 'status': response.status_code}
                    
        except Exception as e:
            print(f"❌ {endpoint} error: {str(e)}")
            endpoint_results[endpoint] = {'type': 'exception', 'error': str(e)}
    
    # STEP 3: Analyze results
    print(f"\n🎯 ANALYSIS OF ALL ENDPOINTS")
    print("-" * 40)
    
    for endpoint, result in endpoint_results.items():
        print(f"\n{endpoint}:")
        print(f"  Type: {result.get('type')}")
        
        if result.get('type') in ['direct', 'progressive']:
            sentences = result.get('sentences', 0)
            issues = result.get('issues', 0)
            print(f"  Sentences: {sentences}")
            print(f"  Issues: {issues}")
            
            if issues == 0:
                print(f"  ❌ NO ISSUES - This endpoint is broken")
            elif issues < 10:
                print(f"  ⚠️  FEW ISSUES - May be filtering out some issue types")
            else:
                print(f"  ✅ GOOD ISSUES - This endpoint is working")
        
        else:
            print(f"  Status: {result}")
    
    # STEP 4: Check which endpoint the frontend actually uses
    print(f"\n🔧 FRONTEND ENDPOINT INVESTIGATION")
    print("-" * 40)
    
    # Check the HTML template to see which endpoint is used
    try:
        with open('app/templates/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Look for the primary upload function
        if "fetch('/upload_progressive'" in html_content:
            print(f"✅ Frontend primarily uses: /upload_progressive")
            working_endpoint = endpoint_results.get('/upload_progressive', {})
            
            if working_endpoint.get('issues', 0) > 0:
                print(f"✅ /upload_progressive is working with {working_endpoint.get('issues')} issues")
                print(f"💡 The issue might be in the frontend JavaScript processing")
            else:
                print(f"❌ /upload_progressive is not working correctly")
                print(f"💡 This is why you're only seeing passive voice - the endpoint is broken")
        
        elif "fetch('/upload'" in html_content:
            print(f"✅ Frontend primarily uses: /upload")
            working_endpoint = endpoint_results.get('/upload', {})
            
            if working_endpoint.get('issues', 0) > 0:
                print(f"✅ /upload is working with {working_endpoint.get('issues')} issues")
            else:
                print(f"❌ /upload is not working correctly")
        
        else:
            print(f"❓ Could not determine primary frontend endpoint")
            
    except Exception as e:
        print(f"❌ Could not read HTML template: {e}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print(f"\n🎯 FINAL RECOMMENDATION:")
    print(f"Check the JSON files created (response_*.json, final_result_*.json)")
    print(f"to see exactly what each endpoint is returning.")

if __name__ == "__main__":
    final_investigation()
