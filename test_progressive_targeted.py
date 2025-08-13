#!/usr/bin/env python3
"""
TARGETED PROGRESSIVE API TEST
Focus specifically on the progressive upload workflow
"""

import requests
import json
import time

def test_progressive_workflow():
    print("🎯 TARGETED PROGRESSIVE API TEST")
    print("=" * 60)
    
    # Test content with multiple rule triggers
    test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
    
    # Create test file
    test_file = 'progressive_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 Test content length: {len(test_content)} characters")
    print(f"📁 Test file created: {test_file}")
    
    # Step 1: Submit to progressive endpoint
    print(f"\n🚀 STEP 1: Submit to /upload_progressive")
    print("-" * 40)
    
    try:
        url = 'http://127.0.0.1:5000/upload_progressive'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            print(f"📤 Sending request to {url}")
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                analysis_id = result.get('analysis_id')
                success = result.get('success', False)
                
                print(f"✅ Progressive upload succeeded")
                print(f"🆔 Analysis ID: {analysis_id}")
                print(f"✅ Success flag: {success}")
                
                if not analysis_id:
                    print(f"❌ No analysis_id returned!")
                    return
                
            else:
                print(f"❌ Progressive upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return
                
    except Exception as e:
        print(f"❌ Error in progressive upload: {e}")
        return
    
    # Step 2: Poll progress endpoint with detailed logging
    print(f"\n📊 STEP 2: Poll /analysis_progress/{analysis_id}")
    print("-" * 40)
    
    progress_url = f'http://127.0.0.1:5000/analysis_progress/{analysis_id}'
    
    max_attempts = 30  # 30 attempts = 1 minute
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        try:
            print(f"\n🔄 Attempt {attempt}/{max_attempts}")
            progress_response = requests.get(progress_url, timeout=10)
            
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                
                stage = progress_data.get('stage', 'unknown')
                percentage = progress_data.get('percentage', 0)
                message = progress_data.get('message', 'No message')
                completed = progress_data.get('completed', False)
                error = progress_data.get('error')
                has_result = 'result' in progress_data and progress_data['result'] is not None
                
                print(f"  📊 Stage: {stage}")
                print(f"  📈 Progress: {percentage}%")
                print(f"  💬 Message: {message}")
                print(f"  ✅ Completed: {completed}")
                print(f"  📄 Has Result: {has_result}")
                
                if error:
                    print(f"  ❌ Error: {error}")
                    break
                
                if completed:
                    print(f"\n🎉 Analysis completed!")
                    
                    if has_result:
                        result_data = progress_data['result']
                        
                        # Analyze the result structure
                        print(f"📄 Result analysis:")
                        print(f"  - Type: {type(result_data)}")
                        print(f"  - Keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'not dict'}")
                        
                        if isinstance(result_data, dict):
                            sentences = result_data.get('sentences', [])
                            report = result_data.get('report', {})
                            content = result_data.get('content', '')
                            
                            print(f"  - Sentences: {len(sentences)}")
                            print(f"  - Content length: {len(content)}")
                            print(f"  - Report keys: {list(report.keys())}")
                            
                            # Count total issues
                            total_issues = sum(len(s.get('feedback', [])) for s in sentences)
                            print(f"  - Total issues found: {total_issues}")
                            
                            # Show issue breakdown by type
                            issue_types = {}
                            for sentence in sentences:
                                for issue in sentence.get('feedback', []):
                                    message = issue.get('message', '').lower()
                                    if 'passive voice' in message:
                                        issue_types['passive_voice'] = issue_types.get('passive_voice', 0) + 1
                                    elif 'long sentence' in message:
                                        issue_types['long_sentence'] = issue_types.get('long_sentence', 0) + 1
                                    elif 'modifier' in message:
                                        issue_types['modifier'] = issue_types.get('modifier', 0) + 1
                                    elif 'utilization' in message or 'terminology' in message:
                                        issue_types['complex_words'] = issue_types.get('complex_words', 0) + 1
                                    else:
                                        issue_types['other'] = issue_types.get('other', 0) + 1
                            
                            print(f"📊 Issue breakdown:")
                            for issue_type, count in issue_types.items():
                                print(f"  - {issue_type}: {count}")
                            
                            # Save the complete result for inspection
                            with open('progressive_final_result.json', 'w', encoding='utf-8') as rf:
                                json.dump(result_data, rf, indent=2, ensure_ascii=False)
                            print(f"💾 Complete result saved to: progressive_final_result.json")
                            
                            # Show first few issues as examples
                            print(f"\n📝 Sample issues:")
                            issue_count = 0
                            for i, sentence in enumerate(sentences):
                                for j, issue in enumerate(sentence.get('feedback', [])):
                                    if issue_count < 5:  # Show first 5 issues
                                        print(f"  {issue_count + 1}. Sentence {i + 1}: {issue.get('message', 'No message')}")
                                        issue_count += 1
                            
                            if total_issues == 0:
                                print(f"\n❌ PROBLEM IDENTIFIED: Progressive endpoint returned 0 issues!")
                                print(f"   But we know the backend can detect 21+ issues.")
                                print(f"   This confirms the progressive endpoint is broken.")
                            else:
                                print(f"\n✅ SUCCESS: Progressive endpoint returned {total_issues} issues!")
                                print(f"   This should show up in the web interface.")
                        
                    else:
                        print(f"❌ Analysis completed but no result data found!")
                    break
                
                # Wait before next attempt
                time.sleep(2)
                
            else:
                print(f"❌ Progress request failed: {progress_response.status_code}")
                print(f"Response: {progress_response.text}")
                break
                
        except Exception as e:
            print(f"❌ Error checking progress: {e}")
            time.sleep(2)
            continue
    
    else:
        print(f"\n⏰ Timeout: Analysis didn't complete in {max_attempts * 2} seconds")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print(f"\n🎯 TEST COMPLETE")

if __name__ == "__main__":
    test_progressive_workflow()
