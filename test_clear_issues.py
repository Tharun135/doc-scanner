#!/usr/bin/env python3
"""
Test the updated rules to ensure they provide clear issue descriptions
"""

import requests
import json

def test_clear_issue_descriptions():
    """Test that rules now provide clear issue descriptions instead of confusing rewrites"""
    
    # Start the app first and then test with a sample document
    test_sentences = [
        {
            "text": "The report was completed by the team yesterday.",
            "expected_issues": ["passive voice", "convert to active"]
        },
        {
            "text": "You have have selected the option for the device.",
            "expected_issues": ["repeated word", "have appears"]
        },
        {
            "text": "The document has been created by the administrator and it must be configured properly.",
            "expected_issues": ["long sentence", "passive voice", "perfect tense"]
        }
    ]
    
    print("🧪 Testing Clear Issue Descriptions")
    print("=" * 60)
    
    for i, test_case in enumerate(test_sentences, 1):
        print(f"\n{i}. Testing: {test_case['text']}")
        print(f"   Expected issue types: {', '.join(test_case['expected_issues'])}")
        
        # Test with document analysis
        data = {"content": test_case['text']}
        
        try:
            response = requests.post('http://127.0.0.1:5000/upload', 
                                   files={'file': ('test.txt', test_case['text'], 'text/plain')})
            
            if response.status_code == 200:
                result = response.json()
                sentences = result.get('sentences', [])
                
                if sentences and len(sentences) > 0:
                    feedback = sentences[0].get('feedback', [])
                    
                    if feedback:
                        print(f"   ✅ Found {len(feedback)} issue(s):")
                        for j, issue in enumerate(feedback):
                            message = issue.get('message', 'N/A')
                            print(f"      {j+1}. {message}")
                            
                            # Check if the message is clear and descriptive
                            if any(expected in message.lower() for expected in test_case['expected_issues']):
                                print(f"         ✅ Clear issue description found")
                            else:
                                print(f"         ⚠️  Issue description could be clearer")
                                
                            # Check if it's NOT a rewritten sentence (bad)
                            if message.startswith('"') and message.endswith('"'):
                                print(f"         ❌ Looks like a rewritten sentence (bad)")
                            elif "you select" in message.lower() and "makes" in message.lower():
                                print(f"         ❌ Contains confusing rewrite pattern (bad)")
                            else:
                                print(f"         ✅ Not a confusing rewrite")
                    else:
                        print(f"   ⚠️  No issues detected")
                else:
                    print(f"   ❌ No sentences returned")
            else:
                print(f"   ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_clear_issue_descriptions()
