#!/usr/bin/env python3
"""
JSON Structure Debug Script
Check the exact structure of the JSON response
"""

import requests
import json

def debug_json_structure():
    """Debug the exact JSON structure"""
    
    # Test content
    test_content = "This document contains writing issues. The passive voice was used extensively throughout this document."
    
    # Save test content to file
    test_file = 'json_debug_test.txt'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    url = 'http://127.0.0.1:5000/upload'
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            data = {'documentType': 'technical'}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Save the full JSON response for inspection
                with open('debug_response.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print("✅ Full JSON response saved to 'debug_response.json'")
                
                # Print first sentence feedback structure
                if 'sentences' in result and len(result['sentences']) > 0:
                    first_sentence = result['sentences'][0]
                    print(f"\nFirst sentence structure:")
                    print(f"Keys: {list(first_sentence.keys())}")
                    
                    if 'feedback' in first_sentence:
                        feedback = first_sentence['feedback']
                        print(f"Feedback type: {type(feedback)}")
                        print(f"Feedback length: {len(feedback) if isinstance(feedback, list) else 'Not a list'}")
                        
                        if isinstance(feedback, list) and len(feedback) > 0:
                            print(f"First feedback item type: {type(feedback[0])}")
                            print(f"First feedback item: {feedback[0]}")
                            
                            if isinstance(feedback[0], dict):
                                print(f"First feedback keys: {list(feedback[0].keys())}")
                        
                # Also check other sentences
                for i, sentence in enumerate(result['sentences']):
                    print(f"\nSentence {i+1}:")
                    print(f"  Feedback exists: {'feedback' in sentence}")
                    if 'feedback' in sentence:
                        feedback = sentence['feedback']
                        if isinstance(feedback, list):
                            print(f"  Feedback count: {len(feedback)}")
                            if len(feedback) > 0:
                                print(f"  First feedback: {feedback[0] if isinstance(feedback[0], str) else str(feedback[0])[:100]}...")
                        else:
                            print(f"  Feedback type: {type(feedback)}")
                            print(f"  Feedback: {feedback}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    debug_json_structure()
