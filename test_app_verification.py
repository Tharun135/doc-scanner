#!/usr/bin/env python3
"""
Test the complete application to verify issue display changes.
"""

import requests
import json

def test_application():
    try:
        url = 'http://127.0.0.1:5000/upload'
        
        with open('test_issue_display_verification.txt', 'r') as f:
            content = f.read()
        
        # Create form data
        files = {'file': ('test.txt', content, 'text/plain')}
        response = requests.post(url, files=files)
        
        print(f'Response status: {response.status_code}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ Analysis successful!')
            print(f'Found {len(result.get("sentences", []))} sentences')
            
            # Check the feedback for each sentence
            total_issues = 0
            for i, sentence_data in enumerate(result.get('sentences', [])):
                if sentence_data.get('feedback'):
                    for feedback in sentence_data['feedback']:
                        total_issues += 1
                        message = feedback.get('message', '')
                        print(f'\nIssue {total_issues}: {message}')
                        
                        # Check if it contains original sentence or AI suggestion  
                        if 'Original sentence:' in message:
                            print('  ❌ FAIL: Contains original sentence')
                            return False
                        elif 'AI suggestion:' in message:
                            print('  ❌ FAIL: Contains AI suggestion in issue')
                            return False
                        else:
                            print('  ✅ PASS: Clean issue description')
            
            print(f'\n✅ SUCCESS: All {total_issues} issues have clean descriptions!')
            return True
        else:
            print(f'❌ Error response: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Exception: {e}')
        return False

if __name__ == "__main__":
    print("Testing Application - Issue Display Verification")
    print("=" * 60)
    
    if test_application():
        print("\n🎉 All tests passed! Issues now only show descriptions.")
    else:
        print("\n❌ Some tests failed.")
