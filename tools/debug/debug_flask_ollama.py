#!/usr/bin/env python3
"""
Debug Flask server ollama_rag_direct execution with detailed logging.
"""

import requests
import json

def debug_flask_ollama_execution():
    """Make a request to Flask and check detailed execution."""
    
    print("🔍 DEBUGGING FLASK OLLAMA_RAG_DIRECT EXECUTION")
    print("=" * 45)
    
    # Test data that should trigger ollama_rag_direct
    test_data = {
        'feedback': 'passive voice detected by rule',
        'sentence': 'The file was saved by the user.'
    }
    
    print(f"📝 Request data:")
    print(f"   Feedback: '{test_data['feedback']}'")
    print(f"   Sentence: '{test_data['sentence']}'")
    
    # Check if this should trigger ollama_rag_direct based on conditions
    feedback_text = test_data['feedback']
    sentence_context = test_data['sentence']
    
    condition1 = "detected by rule" in feedback_text.lower()
    condition2 = "rule" in feedback_text.lower() 
    condition3 = len(sentence_context) > 10
    
    should_trigger = condition1 or condition2 or condition3
    
    print(f"\n📋 Trigger conditions:")
    print(f"   'detected by rule': {condition1}")
    print(f"   'rule' keyword: {condition2}")
    print(f"   sentence > 10 chars: {condition3}")
    print(f"   Should trigger ollama_rag_direct: {should_trigger}")
    
    if not should_trigger:
        print(f"❌ CONDITIONS NOT MET - ollama_rag_direct won't be attempted")
        return
    
    print(f"\n🔄 Making Flask request...")
    
    try:
        # Make the request with a longer timeout to see what happens
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=30  # Long timeout to see the full execution
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Flask response received:")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   AI Answer length: {len(result.get('ai_answer', ''))}")
            print(f"   Suggestion length: {len(result.get('suggestion', ''))}")
            print(f"   Sources: {len(result.get('sources', []))}")
            
            method = result.get('method', '')
            
            if method == 'ollama_rag_direct':
                print(f"\n✅ SUCCESS! ollama_rag_direct worked in Flask!")
                print(f"   AI Answer: '{result.get('ai_answer', '')[:150]}...'")
            elif method.startswith('chromadb'):
                print(f"\n📚 Using RAG fallback: {method}")
                print(f"   This means ollama_rag_direct was attempted but failed")
                print(f"   Likely causes:")
                print(f"     - Timeout during Flask execution")
                print(f"     - ChromaDB query failed")
                print(f"     - Ollama API error in Flask context")
                print(f"     - Exception caught and logged")
            else:
                print(f"\n⚠️ Using non-RAG method: {method}")
            
            # Show some of the actual content
            ai_answer = result.get('ai_answer', '')
            if ai_answer:
                print(f"\n📄 AI Answer preview:")
                print(f"   \"{ai_answer[:200]}...\"")
            
        else:
            print(f"❌ Flask HTTP error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Flask request timed out (30s)")
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_flask_logging():
    """Try to capture Flask server logs during execution."""
    
    print(f"\n📋 FLASK LOGGING INSTRUCTIONS:")
    print(f"=" * 35)
    print(f"To see what's happening in Flask:")
    print(f"1. Check the Flask terminal for log messages")
    print(f"2. Look for '[ENRICH]' prefixed messages")
    print(f"3. Specifically look for:")
    print(f"   - 'Attempting ollama_rag_direct'")
    print(f"   - 'ollama_rag_direct SUCCESS'") 
    print(f"   - 'ollama_rag_direct timeout'")
    print(f"   - 'ollama_rag_direct failed'")
    print(f"4. If no ollama_rag_direct messages appear, the conditions aren't met")

if __name__ == "__main__":
    debug_flask_ollama_execution()
    test_flask_logging()
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Check Flask terminal output during this test")
    print(f"2. If no ollama_rag_direct logs appear, check condition logic")
    print(f"3. If timeout logs appear, increase Flask timeout setting")
    print(f"4. If success logs appear but method != ollama_rag_direct, check response processing")
