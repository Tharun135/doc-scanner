#!/usr/bin/env python3
"""
Quick test of the updated formatting preservation.
"""

import requests
import json
import time

def test_updated_fix():
    """Test the updated sentence processing with HTML preservation."""
    
    print("🔍 TESTING UPDATED HTML PRESERVATION")
    print("=" * 50)
    
    # Simple test with the specific problematic cases
    test_content = """This sentence has **bold words** in the middle.

Here is a sentence with a [link](https://example.com) included.

This contains image reference 176617096203-d2e2393 inline."""
    
    print("📄 Test content:")
    print(test_content)
    print("\n" + "=" * 50)
    
    try:
        print("📤 Testing upload...")
        files = {'file': ('test.md', test_content, 'text/markdown')}
        response = requests.post('http://127.0.0.1:5000/upload_progressive', files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            
            if analysis_id:
                print("✅ Upload successful, checking results...")
                time.sleep(2)
                
                progress_response = requests.get(f'http://127.0.0.1:5000/analysis_progress/{analysis_id}', timeout=10)
                
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    
                    if progress_data.get('status') == 'completed':
                        result_data = progress_data['result']
                        sentences = result_data.get('sentences', [])
                        
                        print(f"\n📊 Found {len(sentences)} sentences:")
                        
                        for i, sentence in enumerate(sentences, 1):
                            text = sentence.get('text', '')
                            html = sentence.get('html_content', '') or sentence.get('content', '')
                            
                            print(f"\nSentence {i}:")
                            print(f"  Text: {text}")
                            print(f"  HTML: {html}")
                            
                            # Check if formatting is preserved
                            has_formatting = ('<strong>' in html or '<a' in html or 
                                            '**' in html or '[' in html)
                            print(f"  Has Formatting: {has_formatting}")
                        
                        # Check specific cases
                        bold_preserved = any('bold words' in s.get('text', '') and 
                                           ('<strong>' in s.get('html_content', '') or 
                                            '**' in s.get('html_content', '')) 
                                           for s in sentences)
                        link_preserved = any('link' in s.get('text', '') and 
                                           ('<a' in s.get('html_content', '') or 
                                            '[' in s.get('html_content', '')) 
                                           for s in sentences)
                        image_preserved = any('176617096203-d2e2393' in s.get('text', '') 
                                            for s in sentences)
                        
                        print(f"\n🎯 Test Results:")
                        print(f"  Bold preservation: {'✅' if bold_preserved else '❌'}")
                        print(f"  Link preservation: {'✅' if link_preserved else '❌'}")
                        print(f"  Image preservation: {'✅' if image_preserved else '❌'}")
                        
                        if bold_preserved and link_preserved and image_preserved:
                            print("\n🎉 SUCCESS: All formatting elements preserved!")
                        else:
                            print("\n⚠️ PARTIAL: Some formatting may need work")
                    else:
                        print(f"⏳ Analysis status: {progress_data.get('status')}")
                else:
                    print(f"❌ Progress check failed: {progress_response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_updated_fix()
