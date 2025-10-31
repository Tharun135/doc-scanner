#!/usr/bin/env python3
"""
Debug AI response extraction issues.
"""

import requests
import json

def debug_ai_extraction():
    """Debug AI response extraction patterns."""
    
    print("🔍 DEBUGGING AI RESPONSE EXTRACTION")
    print("=" * 40)
    
    # Test a specific case that showed problems
    test_case = {
        "feedback": "passive voice detected by rule",
        "sentence": "The file was uploaded by the user."
    }
    
    print(f"📝 Testing: \"{test_case['sentence']}\"")
    print(f"🔍 Feedback: \"{test_case['feedback']}\"")
    
    try:
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_case,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            method = result.get('method', 'unknown')
            ai_answer = result.get('ai_answer', '')
            suggestion = result.get('suggestion', '')
            sources = result.get('sources', [])
            
            print(f"\n📊 RESULTS:")
            print(f"   Method: {method}")
            print(f"   Sources: {len(sources)}")
            
            print(f"\n🤖 RAW AI RESPONSE:")
            print(f'   "{ai_answer}"')
            
            print(f"\n💡 EXTRACTED SUGGESTION:")
            print(f'   "{suggestion}"')
            
            # Analyze the extraction
            print(f"\n🔍 EXTRACTION ANALYSIS:")
            
            if '[' in ai_answer and ']' in ai_answer:
                print(f"   ✅ Contains brackets - should extract bracketed content")
                # Extract what's in brackets
                import re
                bracket_match = re.search(r'\[([^\]]+)\]', ai_answer)
                if bracket_match:
                    bracket_content = bracket_match.group(1)
                    print(f"   📝 Bracket content: \"{bracket_content}\"")
            
            if '"' in ai_answer:
                print(f"   ✅ Contains quotes - should extract quoted content")
                quotes = re.findall(r'"([^"]+)"', ai_answer)
                for i, quote in enumerate(quotes):
                    print(f"   📝 Quote {i+1}: \"{quote}\"")
            
            if 'rewrite:' in ai_answer.lower():
                print(f"   ✅ Contains 'rewrite:' pattern")
                rewrite_index = ai_answer.lower().find('rewrite:')
                after_rewrite = ai_answer[rewrite_index + len('rewrite:'):].strip()
                print(f"   📝 After 'rewrite:': \"{after_rewrite[:100]}...\"")
            
            # Check what the actual extraction should be
            print(f"\n🎯 EXPECTED EXTRACTION:")
            print(f"   Input: \"{test_case['sentence']}\"")
            print(f"   Expected: Something like \"The user uploaded the file.\"")
            print(f"   Actual: \"{suggestion}\"")
            
            if suggestion == test_case['sentence']:
                print(f"   ❌ PROBLEM: Suggestion is same as input!")
            elif len(suggestion) < 10:
                print(f"   ❌ PROBLEM: Suggestion is too short!")
            elif "uploadeds" in suggestion or suggestion.endswith("uploads."):
                print(f"   ❌ PROBLEM: Grammar issues in extraction!")
            else:
                print(f"   ✅ Extraction seems reasonable")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_direct_ollama():
    """Test direct Ollama API call to see raw response."""
    
    print(f"\n🤖 DIRECT OLLAMA TEST")
    print("=" * 25)
    
    test_prompt = """Convert this passive voice to active voice:

"The file was uploaded by the user."

Rewrite: [provide the active voice version]"""
    
    print(f"📝 Prompt:")
    print(f"   {test_prompt}")
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'tinyllama:latest',
            'prompt': test_prompt,
            'stream': False,
            'options': {
                'temperature': 0.1,
                'top_p': 0.8,
                'num_predict': 120,
                'num_ctx': 1500,
                'repeat_penalty': 1.1,
                'mirostat': 0
            }
        }, timeout=25)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            print(f"\n🤖 DIRECT OLLAMA RESPONSE:")
            print(f'   "{ai_response}"')
            
            # Test extraction patterns on this response
            print(f"\n🔍 EXTRACTION PATTERN TESTING:")
            
            # Pattern 1: Bracketed content
            if '[' in ai_response and ']' in ai_response:
                import re
                bracket_matches = re.findall(r'\[([^\]]+)\]', ai_response)
                print(f"   Bracket matches: {bracket_matches}")
            
            # Pattern 2: After "Rewrite:"
            if 'rewrite:' in ai_response.lower():
                rewrite_index = ai_response.lower().find('rewrite:')
                after_rewrite = ai_response[rewrite_index + len('rewrite:'):].strip()
                # Clean up
                clean_text = after_rewrite.replace('[', '').replace(']', '').replace('"', '').strip()
                print(f"   After 'Rewrite:': \"{clean_text}\"")
            
            # Pattern 3: Quoted content
            if '"' in ai_response:
                quotes = re.findall(r'"([^"]+)"', ai_response)
                print(f"   Quoted content: {quotes}")
            
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    debug_ai_extraction()
    test_direct_ollama()
