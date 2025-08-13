#!/usr/bin/env python3
"""
Debug what's actually being sent to the web interface
"""

import requests
import json
import time

def test_actual_upload():
    """Test what the upload endpoint actually returns"""
    
    # Wait for server to be ready
    time.sleep(3)
    
    # Test content with multiple rule triggers - same as what user might test
    test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
    
    # Save to file
    test_file = 'actual_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("🔍 DEBUGGING ACTUAL WEB UPLOAD")
    print("=" * 70)
    print(f"Test content:")
    print(f"{test_content}")
    print("=" * 70)
    
    url = 'http://127.0.0.1:5000/upload'
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            print("📤 Sending request to Flask server...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Save full response for inspection
                with open('actual_response.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Response received and saved to 'actual_response.json'")
                
                if 'sentences' in result:
                    sentences = result['sentences']
                    print(f"\n📊 ANALYSIS RESULTS:")
                    print(f"Number of sentences: {len(sentences)}")
                    
                    total_issues = 0
                    issue_breakdown = {}
                    
                    for i, sentence in enumerate(sentences):
                        feedback = sentence.get('feedback', [])
                        sentence_text = sentence.get('sentence', '')
                        
                        print(f"\n--- Sentence {i+1} ---")
                        print(f"Text: '{sentence_text[:80]}{'...' if len(sentence_text) > 80 else ''}'")
                        print(f"Issues found: {len(feedback)}")
                        
                        if feedback:
                            for j, issue in enumerate(feedback):
                                if isinstance(issue, dict):
                                    message = issue.get('message', 'No message')
                                    print(f"  {j+1}. {message[:100]}{'...' if len(message) > 100 else ''}")
                                    
                                    # Categorize issues
                                    if 'passive voice' in message.lower():
                                        issue_breakdown['Passive Voice'] = issue_breakdown.get('Passive Voice', 0) + 1
                                    elif 'long sentence' in message.lower():
                                        issue_breakdown['Long Sentence'] = issue_breakdown.get('Long Sentence', 0) + 1
                                    elif 'modifier' in message.lower() and 'very' in message.lower():
                                        issue_breakdown['Unnecessary Modifiers'] = issue_breakdown.get('Unnecessary Modifiers', 0) + 1
                                    elif 'verbose' in message.lower() or 'utiliz' in message.lower():
                                        issue_breakdown['Verbose Language'] = issue_breakdown.get('Verbose Language', 0) + 1
                                    elif 'weak verb' in message.lower():
                                        issue_breakdown['Weak Verbs'] = issue_breakdown.get('Weak Verbs', 0) + 1
                                    else:
                                        issue_breakdown['Other'] = issue_breakdown.get('Other', 0) + 1
                                else:
                                    print(f"  {j+1}. {str(issue)[:100]}...")
                        else:
                            print("  No issues detected for this sentence")
                        
                        total_issues += len(feedback)
                    
                    print(f"\n🎯 FINAL SUMMARY:")
                    print(f"Total issues across all sentences: {total_issues}")
                    print(f"\nIssue breakdown by type:")
                    for issue_type, count in issue_breakdown.items():
                        print(f"  {issue_type}: {count}")
                    
                    if total_issues == 0:
                        print("\n❌ NO ISSUES DETECTED - This indicates a problem with the backend")
                    elif len(issue_breakdown) == 1 and 'Passive Voice' in issue_breakdown:
                        print("\n⚠️  ONLY PASSIVE VOICE DETECTED - Other rules not working")
                        print("   This confirms your reported issue!")
                    elif len(issue_breakdown) > 1:
                        print("\n✅ MULTIPLE ISSUE TYPES DETECTED - Backend working correctly")
                        print("   If you're not seeing this in browser, it's a frontend issue")
                    
                else:
                    print("❌ No 'sentences' key in response")
                    print(f"Response keys: {list(result.keys())}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_actual_upload()
