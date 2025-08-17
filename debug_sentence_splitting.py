#!/usr/bin/env python3
"""
Debug the exact sentence splitting issue to understand where the problem is occurring.
"""

import requests
import json
import time

def debug_sentence_splitting():
    """Debug exactly how sentences are being split incorrectly."""
    
    print("🔍 DEBUGGING SENTENCE SPLITTING ISSUE")
    print("=" * 70)
    
    # Test with the exact example you provided
    test_content = """You can choose to set any project to Autostart mode by activating the **Enable Autostart** option."""
    
    print("📄 Test content:")
    print(f'"{test_content}"')
    print("\nExpected: 1 sentence")
    print("Problem: Being split into 3 sentences")
    print("\n" + "=" * 70)
    
    try:
        print("📤 Testing upload...")
        files = {'file': ('debug_test.md', test_content, 'text/markdown')}
        response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            
            if analysis_id:
                print("✅ Upload successful, checking results...")
                time.sleep(3)  # Give it time to process
                
                progress_response = requests.get(f'http://127.0.0.1:5000/analysis_progress/{analysis_id}', timeout=15)
                
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    
                    if progress_data.get('status') == 'completed':
                        result_data = progress_data['result']
                        sentences = result_data.get('sentences', [])
                        
                        print(f"\n🚨 PROBLEM IDENTIFIED:")
                        print(f"Found {len(sentences)} sentences (should be 1)")
                        print("\nDetailed breakdown:")
                        
                        for i, sentence in enumerate(sentences, 1):
                            text = sentence.get('text', '')
                            html = sentence.get('html_content', '') or sentence.get('content', '')
                            
                            print(f"\nSentence {i}:")
                            print(f"  Text: '{text}'")
                            print(f"  HTML: '{html}'")
                            print(f"  Length: {len(text)} chars")
                            
                            # Identify the problematic parts
                            if "Enable Autostart" in text and len(text) < 20:
                                print("  🚨 THIS IS THE SPLIT BOLD TEXT!")
                            elif "activating the" in text and "option" not in text:
                                print("  🚨 THIS IS THE FIRST PART BEFORE BOLD!")
                            elif text.strip() == "option.":
                                print("  🚨 THIS IS THE LAST PART AFTER BOLD!")
                        
                        # Analysis
                        print(f"\n📊 ANALYSIS:")
                        if len(sentences) == 3:
                            print("✅ Confirmed: The sentence is being split around the bold text")
                            print("❌ Issue: Bold formatting is treated as sentence boundary")
                        elif len(sentences) == 1:
                            print("✅ Fixed: Sentence is properly preserved!")
                        else:
                            print(f"❓ Unexpected: Found {len(sentences)} sentences")
                            
                        print(f"\n💡 ROOT CAUSE:")
                        print("The text extraction or sentence splitting logic is breaking")
                        print("sentences at formatting boundaries instead of periods only.")
                        
                    else:
                        print(f"⏳ Analysis status: {progress_data.get('status')}")
                        print(f"Progress: {progress_data.get('progress', 0)}%")
                else:
                    print(f"❌ Progress check failed: {progress_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sentence_splitting()
