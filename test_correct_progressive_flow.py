#!/usr/bin/env python3
"""
CORRECT API FLOW TEST
The progressive analysis works in 2 steps:
1. POST /upload_progressive -> returns analysis_id
2. GET /analysis_progress/<analysis_id> -> returns actual results
"""

import requests
import json
import time
import sys
sys.path.append('app')

def test_correct_progressive_flow():
    """Test the correct 2-step progressive API flow"""
    
    print("🔍 TESTING CORRECT PROGRESSIVE API FLOW")
    print("=" * 80)
    
    # Test content that should trigger multiple rule types
    test_content = """The document was written by the author and it was reviewed extensively by team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding of the content. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed immediately. Furthermore, the implementation was conducted by the development team. The system was designed to facilitate user interaction. Very detailed documentation was provided."""
    
    print(f"📝 Test content: {len(test_content)} chars")
    print("-" * 80)
    
    # Wait for server to be ready
    time.sleep(2)
    
    # STEP 1: Upload file to get analysis_id
    print("STEP 1: Uploading file to /upload_progressive")
    print("-" * 40)
    
    test_file = 'progressive_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        url = 'http://127.0.0.1:5000/upload_progressive'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                upload_result = response.json()
                analysis_id = upload_result.get('analysis_id')
                
                print(f"✅ Upload successful")
                print(f"Analysis ID: {analysis_id}")
                print(f"Success: {upload_result.get('success')}")
                
                if analysis_id:
                    # STEP 2: Poll for analysis results
                    print(f"\nSTEP 2: Polling /analysis_progress/{analysis_id}")
                    print("-" * 40)
                    
                    progress_url = f'http://127.0.0.1:5000/analysis_progress/{analysis_id}'
                    
                    # Poll up to 30 seconds
                    for attempt in range(30):
                        try:
                            progress_response = requests.get(progress_url, timeout=10)
                            
                            if progress_response.status_code == 200:
                                progress_data = progress_response.json()
                                
                                stage = progress_data.get('stage', 'unknown')
                                status = progress_data.get('status', 'unknown')
                                progress_percent = progress_data.get('progress', 0)
                                
                                print(f"Attempt {attempt+1}: Stage={stage}, Status={status}, Progress={progress_percent}%")
                                
                                if status == 'completed':
                                    print(f"\n✅ Analysis completed!")
                                    
                                    # Check for results
                                    if 'result' in progress_data:
                                        result = progress_data['result']
                                        
                                        # Save full results
                                        with open('progressive_results.json', 'w', encoding='utf-8') as f:
                                            json.dump(progress_data, f, indent=2, ensure_ascii=False)
                                        
                                        print(f"📄 Full results saved to 'progressive_results.json'")
                                        
                                        # Analyze results
                                        if 'sentences' in result:
                                            sentences = result['sentences']
                                            analyze_progressive_results(sentences)
                                        else:
                                            print(f"❌ No sentences in result")
                                            print(f"Result keys: {list(result.keys())}")
                                    else:
                                        print(f"❌ No result in progress data")
                                        print(f"Progress data keys: {list(progress_data.keys())}")
                                    
                                    break
                                elif status == 'error':
                                    print(f"❌ Analysis failed with error")
                                    if 'error' in progress_data:
                                        print(f"Error: {progress_data['error']}")
                                    break
                                else:
                                    # Still processing, wait and try again
                                    time.sleep(2)
                            else:
                                print(f"❌ Progress check failed: {progress_response.status_code}")
                                break
                                
                        except Exception as e:
                            print(f"❌ Progress check error: {e}")
                            break
                    else:
                        print(f"❌ Analysis timed out after 30 attempts")
                        
                else:
                    print(f"❌ No analysis_id in upload response")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Upload failed: {e}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

def analyze_progressive_results(sentences):
    """Analyze the results from the progressive API"""
    
    print(f"\n🔍 ANALYZING PROGRESSIVE RESULTS")
    print("-" * 40)
    
    print(f"Total sentences: {len(sentences)}")
    
    total_issues = 0
    issue_categories = {}
    
    for i, sentence in enumerate(sentences):
        feedback = sentence.get('feedback', [])
        total_issues += len(feedback)
        
        print(f"\nSentence {i+1}: {len(feedback)} issues")
        sentence_text = sentence.get('text', '')[:60]
        print(f"  Text: {sentence_text}...")
        
        if feedback:
            for j, issue in enumerate(feedback):
                message = issue.get('message', 'No message')
                rule_type = issue.get('rule_type', 'Unknown')
                
                if j < 3:  # Show first 3 issues
                    print(f"    {j+1}. [{rule_type}] {message[:70]}...")
                
                # Categorize issues
                message_lower = message.lower()
                if 'passive voice' in message_lower:
                    issue_categories['passive_voice'] = issue_categories.get('passive_voice', 0) + 1
                elif 'long sentence' in message_lower or 'breaking' in message_lower:
                    issue_categories['long_sentence'] = issue_categories.get('long_sentence', 0) + 1
                elif 'modifier' in message_lower:
                    issue_categories['modifier'] = issue_categories.get('modifier', 0) + 1
                elif 'weak verb' in message_lower or 'nominalization' in message_lower:
                    issue_categories['weak_verb'] = issue_categories.get('weak_verb', 0) + 1
                elif 'verbose' in message_lower or 'utiliz' in message_lower or 'simplif' in message_lower:
                    issue_categories['verbose'] = issue_categories.get('verbose', 0) + 1
                else:
                    issue_categories['other'] = issue_categories.get('other', 0) + 1
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Total issues detected: {total_issues}")
    print(f"Issue categories: {issue_categories}")
    print(f"Number of categories: {len(issue_categories)}")
    
    if len(issue_categories) == 1 and 'passive_voice' in issue_categories:
        print(f"\n❌ PROBLEM CONFIRMED: Only passive voice detected")
        print(f"   The progressive API is also filtering out other issue types")
    elif len(issue_categories) > 1:
        print(f"\n✅ SUCCESS: Multiple issue types detected")
        print(f"   Progressive API is working correctly")
    else:
        print(f"\n❓ UNEXPECTED: No issues or unknown pattern")

if __name__ == "__main__":
    test_correct_progressive_flow()
