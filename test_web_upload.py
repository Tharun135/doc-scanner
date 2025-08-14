#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

import requests
import json
from io import BytesIO

def test_web_upload():
    """Test the actual web upload to see if the issue is really fixed."""
    
    # Markdown content with all the problematic cases
    test_content = """# Test Document for All Issues

This is a normal sentence without any formatting.

This sentence has a **bold word** in the middle and should stay together.

This sentence contains an image reference 176617096203-d2e2393 which should not split.

This sentence has a [link to example](https://example.com) which should also stay together.

This complex sentence has **bold text**, an image 987654321-test, and a [link](https://test.com) all together.

Another sentence with [multiple links](https://first.com) and [second link](https://second.com) should work.

Final sentence with **bold**, `code`, image 123456789-final, and [link](https://final.com) combined.
"""
    
    # Save to file for upload
    with open('test_upload.md', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Upload to the web server
    url = 'http://127.0.0.1:5000/upload'
    
    try:
        with open('test_upload.md', 'rb') as f:
            files = {'file': ('test_upload.md', f, 'text/markdown')}
            
            print("Uploading file to web server...")
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                print("=== WEB UPLOAD SUCCESSFUL ===")
                print(f"Status: {response.status_code}")
                
                # Extract sentence information
                if 'sentences' in result:
                    sentences = result['sentences']
                    print(f"\n=== SENTENCES FROM WEB SERVER ({len(sentences)} total) ===")
                    for i, sentence in enumerate(sentences):
                        print(f"{i+1}: '{sentence['text']}'")
                        
                    # Check for problematic splits
                    problems = []
                    for i, sentence in enumerate(sentences):
                        text = sentence['text']
                        # Check if sentences are incorrectly split
                        if (text.strip() in ['bold word', 'bold text', 'bold', 'code', 'link', 'multiple links', 'second link'] or
                            text.strip().endswith('has a') or 
                            text.strip().endswith('sentence with') or
                            text.strip().endswith('Final sentence with')):
                            problems.append(f"Sentence {i+1}: '{text}' - looks like incorrect split")
                    
                    if problems:
                        print(f"\n=== PROBLEMS DETECTED ({len(problems)}) ===")
                        for problem in problems:
                            print(f"❌ {problem}")
                        print("\n🔍 The issue is NOT fixed - sentences are still being split incorrectly!")
                    else:
                        print(f"\n=== NO SPLITTING PROBLEMS DETECTED ===")
                        print("✅ The fix appears to be working correctly!")
                        
                    # Also check the total number - should be around 8 sentences, not 20+
                    if len(sentences) > 15:
                        print(f"\n⚠️  WARNING: Too many sentences ({len(sentences)}) - suggests splitting is still occurring")
                    else:
                        print(f"\n✅ Sentence count ({len(sentences)}) looks reasonable")
                        
                else:
                    print("No 'sentences' key in response")
                    print("Response keys:", list(result.keys()))
                    
            else:
                print(f"Upload failed with status {response.status_code}")
                print("Response:", response.text)
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error during upload: {e}")

if __name__ == "__main__":
    test_web_upload()
