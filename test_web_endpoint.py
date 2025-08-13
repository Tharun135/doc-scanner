#!/usr/bin/env python3
"""
Test the Flask web app endpoint directly
"""

import requests
import json
import io

def test_web_endpoint():
    """Test the Flask web app endpoint directly."""
    
    url = "http://127.0.0.1:5000/upload"
    
    # Test text with obvious issues
    test_text = "The document was written by the team and the system was configured by the admin. This is a very long sentence that contains many words and clauses and should definitely be detected as being too long for good readability."
    
    print("=== TESTING FLASK WEB ENDPOINT ===")
    print(f"URL: {url}")
    print(f"Text: {test_text}")
    print()
    
    try:
        # Create a fake file object with our test text
        file_content = test_text.encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        # Send POST request with file upload
        files = {
            'file': ('test_document.txt', file_obj, 'text/plain')
        }
        
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("JSON Response Keys:", list(result.keys()))
                
                # Check for sentences (the main analysis result)
                if 'sentences' in result:
                    sentences = result['sentences']
                    print(f"\nNumber of sentences analyzed: {len(sentences)}")
                    
                    total_issues = 0
                    for i, sentence_data in enumerate(sentences):
                        feedback = sentence_data.get('feedback', [])
                        if feedback:
                            print(f"\nSentence {i+1}: '{sentence_data.get('sentence', '')[:50]}...'")
                            print(f"  Issues found: {len(feedback)}")
                            for j, issue in enumerate(feedback):
                                print(f"    {j+1}. {issue.get('message', str(issue))}")
                            total_issues += len(feedback)
                        else:
                            print(f"Sentence {i+1}: No issues")
                    
                    print(f"\nTOTAL ISSUES FOUND: {total_issues}")
                    
                    # Check report
                    if 'report' in result:
                        report = result['report']
                        print(f"Quality Score: {report.get('avgQualityScore', 'N/A')}")
                        print(f"Total Sentences: {report.get('totalSentences', 'N/A')}")
                        print(f"Total Words: {report.get('totalWords', 'N/A')}")
                else:
                    print("No 'sentences' key in response")
                    print("Available keys:", list(result.keys()))
                    
            except json.JSONDecodeError:
                print("Response is not JSON:")
                print(response.text[:500])
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_endpoint()
