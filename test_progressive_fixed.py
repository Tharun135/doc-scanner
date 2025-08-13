#!/usr/bin/env python3
"""
Test the FIXED progressive upload endpoint
"""

import requests
import json
import time

def test_progressive_upload():
    """Test the fixed progressive upload endpoint"""
    
    print("🔍 TESTING FIXED PROGRESSIVE UPLOAD ENDPOINT")
    print("=" * 60)
    
    # Wait for server
    time.sleep(3)
    
    # Test content that should trigger multiple rules
    test_content = """The document was written by the author. It was reviewed extensively by the team members. This is a very long sentence that continues to go on and on without any clear purpose or direction, making it extremely difficult for readers to follow the main point which becomes problematic for clarity and understanding. The utilization of complex terminology makes the document harder to understand. Additionally, there are very important points that need to be addressed. Furthermore, the implementation was conducted by the development team."""
    
    # Create test file
    test_file = 'progressive_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"Test content: {test_content[:100]}...")
    print("=" * 60)
    
    try:
        # Test the progressive upload endpoint (this is what the web interface uses)
        url = 'http://127.0.0.1:5000/upload_progressive'
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            print("📤 Sending request to /upload_progressive...")
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Save response for inspection
                with open('progressive_response.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Progressive upload response saved to 'progressive_response.json'")
                
                if 'sentences' in result:
                    sentences = result['sentences']
                    print(f"\n📊 PROGRESSIVE ANALYSIS RESULTS:")
                    print(f"Number of sentences: {len(sentences)}")
                    
                    total_issues = 0
                    issue_types = {}
                    
                    for i, sentence in enumerate(sentences):
                        feedback = sentence.get('feedback', [])
                        sentence_text = sentence.get('sentence', '')
                        
                        print(f"\n--- Sentence {i+1} ---")
                        print(f"Text: '{sentence_text[:60]}{'...' if len(sentence_text) > 60 else ''}'")
                        print(f"Issues found: {len(feedback)}")
                        
                        if feedback:
                            for j, issue in enumerate(feedback[:3]):  # Show first 3
                                if isinstance(issue, dict):
                                    message = issue.get('message', 'No message')
                                    print(f"  {j+1}. {message[:80]}{'...' if len(message) > 80 else ''}")
                                    
                                    # Categorize issues
                                    message_lower = message.lower()
                                    if 'passive voice' in message_lower:
                                        issue_types['Passive Voice'] = issue_types.get('Passive Voice', 0) + 1
                                    elif 'long sentence' in message_lower:
                                        issue_types['Long Sentence'] = issue_types.get('Long Sentence', 0) + 1
                                    elif 'modifier' in message_lower:
                                        issue_types['Unnecessary Modifiers'] = issue_types.get('Unnecessary Modifiers', 0) + 1
                                    elif 'weak verb' in message_lower:
                                        issue_types['Weak Verbs'] = issue_types.get('Weak Verbs', 0) + 1
                                    elif 'verbose' in message_lower or 'utiliz' in message_lower:
                                        issue_types['Verbose Language'] = issue_types.get('Verbose Language', 0) + 1
                                    else:
                                        issue_types['Other'] = issue_types.get('Other', 0) + 1
                                else:
                                    print(f"  {j+1}. {str(issue)[:80]}...")
                        else:
                            print("  No issues detected for this sentence")
                        
                        total_issues += len(feedback)
                    
                    print(f"\n🎯 FINAL RESULTS:")
                    print(f"Total issues across all sentences: {total_issues}")
                    print(f"\nIssue breakdown by type:")
                    for issue_type, count in issue_types.items():
                        print(f"  {issue_type}: {count}")
                    
                    if total_issues == 0:
                        print(f"\n❌ STILL NO ISSUES - Backend integration failed")
                        print(f"   Check the server logs for errors")
                    elif len(issue_types) == 1 and 'Passive Voice' in issue_types:
                        print(f"\n❌ STILL ONLY PASSIVE VOICE")
                        print(f"   The fix didn't work - need to investigate further")
                    elif len(issue_types) > 1:
                        print(f"\n✅ SUCCESS! MULTIPLE ISSUE TYPES DETECTED!")
                        print(f"   Found {len(issue_types)} different issue types")
                        print(f"   Your web interface should now show multiple issue types!")
                    
                else:
                    print(f"❌ No 'sentences' key in response")
                    print(f"Response keys: {list(result.keys())}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text[:300]}...")
                
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Flask server on http://127.0.0.1:5000")
        print(f"   Make sure the server is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_progressive_upload()
