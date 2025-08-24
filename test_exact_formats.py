#!/usr/bin/env python3
"""
Test with exact same feedback formats that worked before.
"""

import requests
import json

def test_known_working_formats():
    """Test with feedback formats we know trigger ollama_rag_direct."""
    
    print("🎯 TESTING KNOWN WORKING FEEDBACK FORMATS")
    print("=" * 45)
    
    test_cases = [
        {
            "name": "Passive Voice - Rule Format",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was uploaded by the user."
        },
        {
            "name": "System Configuration",
            "feedback": "passive voice detected by rule", 
            "sentence": "The system can be configured by administrators."
        },
        {
            "name": "Click On Issue",
            "feedback": "click on issue detected by rule",
            "sentence": "To save changes, click on the Submit button."
        },
        {
            "name": "Admonition Issue",
            "feedback": "admonition issue detected by rule",
            "sentence": "Note: This feature requires admin privileges."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"   Input: \"{test_case['sentence']}\"")
        print(f"   Feedback: \"{test_case['feedback']}\"")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                sources = result.get('sources', [])
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📊 Method: {method}")
                print(f"   📚 Sources: {len(sources)}")
                print(f"   🤖 AI Answer: \"{ai_answer[:150]}{'...' if len(ai_answer) > 150 else ''}\"")
                print(f"   💡 Suggestion: \"{suggestion[:150]}{'...' if len(suggestion) > 150 else ''}\"")
                
                # Success indicators
                if method == 'ollama_rag_direct':
                    print(f"   🎉 SUCCESS: Using ollama_rag_direct!")
                elif method == 'smart_fallback':
                    print(f"   ⚠️ FALLBACK: Using smart_fallback")
                else:
                    print(f"   ❓ UNKNOWN: Method {method}")
                
                if len(sources) > 0:
                    print(f"   📖 Knowledge sources used:")
                    for j, source in enumerate(sources[:2]):  # Show first 2 sources
                        source_id = source.get('id', 'unknown')
                        source_title = source.get('title', 'No title')
                        print(f"     {j+1}. {source_id}: {source_title}")
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Request timeout (30s exceeded)")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def check_flask_status():
    """Quick check if Flask server is responding."""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"✅ Flask server responding (status: {response.status_code})")
        return True
    except:
        print(f"❌ Flask server not accessible")
        return False

if __name__ == "__main__":
    print("🔍 PRE-TEST SERVER CHECK")
    print("=" * 25)
    
    if check_flask_status():
        test_known_working_formats()
    else:
        print("Please start the Flask server first with: python run.py")
