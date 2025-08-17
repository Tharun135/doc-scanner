#!/usr/bin/env python3
"""Simple test for the fixed sentence processing"""

import requests
import time
import json

def test_upload_fix():
    print("🧪 TESTING UPLOAD PROGRESSIVE FIX")
    print("=" * 50)
    
    # Test content with problematic formatting
    test_content = "You can choose to set any project to Autostart mode by activating the **Enable Autostart** option."
    
    print(f"📄 Test content: {test_content}")
    print(f"✅ Expected: 1 sentence (not split at **Enable Autostart**)")
    print()
    
    # Upload file
    files = {'file': ('test.txt', test_content, 'text/plain')}
    
    try:
        print("📤 Uploading...")
        response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        analysis_id = data.get('analysis_id')
        print(f"✅ Upload successful! Analysis ID: {analysis_id}")
        
        # Wait for completion
        print("⏳ Waiting for analysis...")
        for i in range(20):  # Max 20 seconds
            time.sleep(1)
            try:
                prog_response = requests.get(f'http://127.0.0.1:5000/progress/{analysis_id}', timeout=5)
                if prog_response.status_code == 200:
                    prog_data = prog_response.json()
                    if prog_data.get('completed'):
                        print("✅ Analysis completed!")
                        break
            except:
                pass
        
        # Get results
        result_response = requests.get(f'http://127.0.0.1:5000/result/{analysis_id}', timeout=5)
        if result_response.status_code == 200:
            result = result_response.json()
            sentences = result.get('sentences', [])
            
            print(f"\n🔍 RESULTS:")
            print(f"📊 Found {len(sentences)} sentences")
            
            for i, sentence in enumerate(sentences, 1):
                content = sentence.get('sentence', sentence.get('plain', ''))
                print(f"  {i}. {content}")
            
            # Check if fix worked
            if len(sentences) == 1:
                sentence_text = sentences[0].get('sentence', '')
                if "Enable Autostart" in sentence_text and "option." in sentence_text:
                    print("\n🎉 SUCCESS! Sentence was NOT split at formatting!")
                    print("✅ The fix is working correctly!")
                else:
                    print(f"\n⚠️ Unexpected content: {sentence_text}")
            else:
                print(f"\n❌ FAILED! Expected 1 sentence, got {len(sentences)}")
        else:
            print(f"❌ Failed to get results: {result_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload_fix()
