#!/usr/bin/env python3
"""Test the fixed upload_progressive endpoint with the sentence splitting issue"""

import requests
import json
import time

def test_progressive_fix():
    print("🧪 TESTING PROGRESSIVE ENDPOINT FIX")
    print("=" * 50)
    
    # Test content with the problematic formatting
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option."""
    
    print(f"📄 Test content: {test_content}")
    print(f"📏 Expected: 1 sentence (should NOT split at **Enable Autostart**)")
    print()
    
    # Step 1: Upload file
    print("STEP 1: Uploading test content...")
    files = {'file': ('test.txt', test_content, 'text/plain')}
    
    try:
        response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=15)
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        upload_data = response.json()
        analysis_id = upload_data.get('analysis_id')
        print(f"✅ Upload successful, analysis_id: {analysis_id}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Step 2: Wait for analysis completion
    print("\nSTEP 2: Waiting for analysis completion...")
    max_wait = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            progress_response = requests.get(f'http://127.0.0.1:5000/progress/{analysis_id}', timeout=5)
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                print(f"📊 Progress: {progress_data.get('percentage', 0)}% - {progress_data.get('message', '')}")
                
                if progress_data.get('completed'):
                    print("✅ Analysis completed!")
                    break
                    
        except Exception as e:
            print(f"⚠️ Progress check error: {e}")
        
        time.sleep(1)
    
    # Step 3: Get final results
    print("\nSTEP 3: Getting final results...")
    try:
        result_response = requests.get(f'http://127.0.0.1:5000/result/{analysis_id}', timeout=10)
        if result_response.status_code != 200:
            print(f"❌ Result fetch failed: {result_response.status_code}")
            return
        
        result_data = result_response.json()
        sentences = result_data.get('sentences', [])
        
        print(f"🔍 ANALYSIS RESULTS:")
        print(f"📊 Total sentences found: {len(sentences)}")
        print()
        
        for i, sentence in enumerate(sentences):
            content = sentence.get('content', '')
            plain = sentence.get('sentence', sentence.get('plain', ''))
            print(f"Sentence {i+1}:")
            print(f"  📝 Content: {content}")
            print(f"  📄 Plain: {plain}")
            print()
        
        # Verify the fix
        if len(sentences) == 1:
            sentence_text = sentences[0].get('sentence', '')
            if "Enable Autostart" in sentence_text and "activating the" in sentence_text and "option." in sentence_text:
                print("🎉 SUCCESS! The sentence was NOT split at formatting elements!")
                print("✅ The fix is working correctly!")
            else:
                print("⚠️ Sentence content unexpected:")
                print(f"Content: {sentence_text}")
        else:
            print(f"❌ FAILED! Expected 1 sentence, got {len(sentences)}")
            print("The sentence is still being incorrectly split.")
            
    except Exception as e:
        print(f"❌ Result fetch error: {e}")

if __name__ == "__main__":
    test_progressive_fix()
