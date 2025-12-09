#!/usr/bin/env python3
"""
Debug why ollama_rag_direct isn't working in the enrichment service.
"""

import requests
import json

def test_simple_integration():
    """Test a simple case to see what happens."""
    
    print("🔍 DEBUGGING OLLAMA_RAG_DIRECT INTEGRATION")
    print("=" * 45)
    
    # Simple test case
    test_data = {
        'feedback': 'passive voice detected by rule',
        'sentence': 'The file was saved by the user.'
    }
    
    print(f"📝 Testing with:")
    print(f"   Feedback: '{test_data['feedback']}'")
    print(f"   Sentence: '{test_data['sentence']}'")
    print(f"   This should trigger ollama_rag_direct attempt...")
    
    try:
        print(f"\n🔄 Making request...")
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=25
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response received:")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   AI Answer: \"{result.get('ai_answer', '')[:100]}...\"")
            print(f"   Suggestion: \"{result.get('suggestion', '')[:100]}...\"")
            
            sources = result.get('sources', [])
            if sources:
                print(f"   Sources: {len(sources)} found")
                for i, source in enumerate(sources[:2]):
                    if isinstance(source, dict):
                        print(f"     {i+1}. Rule: {source.get('rule_id', 'unknown')}")
            
            # Check if it tried ollama_rag_direct
            method = result.get('method', '')
            if method == 'ollama_rag_direct':
                print(f"\n🎯 SUCCESS! Got ollama_rag_direct response!")
            elif method.startswith('chromadb'):
                print(f"\n📚 Got RAG fallback: {method}")
                print(f"   This means ollama_rag_direct was attempted but failed/timed out")
            else:
                print(f"\n⚠️ Got basic fallback: {method}")
        
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def check_enrichment_service_directly():
    """Test the enrichment service conditions directly."""
    
    print(f"\n🔧 CHECKING ENRICHMENT SERVICE CONDITIONS")
    print("=" * 45)
    
    # Test the conditions that should trigger ollama_rag_direct
    test_cases = [
        {
            "feedback": "passive voice detected by rule",
            "sentence": "The file was saved by the user.",
            "should_trigger": True,
            "reason": "Contains 'detected by rule'"
        },
        {
            "feedback": "passive voice issue", 
            "sentence": "The file was saved by the user.",
            "should_trigger": False,
            "reason": "No 'rule' keyword"
        },
        {
            "feedback": "rule flagged this issue",
            "sentence": "The file was saved by the user.", 
            "should_trigger": True,
            "reason": "Contains 'rule'"
        }
    ]
    
    print("📋 Testing trigger conditions:")
    
    for i, case in enumerate(test_cases, 1):
        feedback = case['feedback']
        sentence = case['sentence']
        
        # Check the conditions from enrichment service
        condition1 = "detected by rule" in feedback.lower()
        condition2 = "rule" in feedback.lower() 
        condition3 = len(sentence) > 10
        
        should_trigger = condition1 or condition2 or condition3
        
        print(f"\n   Test {i}: '{feedback}'")
        print(f"     'detected by rule': {condition1}")
        print(f"     'rule' keyword: {condition2}")
        print(f"     sentence > 10 chars: {condition3} (len={len(sentence)})")
        print(f"     Should trigger: {should_trigger}")
        print(f"     Expected: {case['should_trigger']} ({case['reason']})")
        
        if should_trigger == case['should_trigger']:
            print(f"     ✅ CONDITION CHECK PASSED")
        else:
            print(f"     ❌ CONDITION CHECK FAILED")

if __name__ == "__main__":
    # Test the conditions first
    check_enrichment_service_directly()
    
    # Then test actual integration
    test_simple_integration()
    
    print(f"\n💡 DEBUGGING SUGGESTIONS:")
    print(f"   1. Check Flask server logs for ollama_rag_direct attempts")
    print(f"   2. Verify Ollama service is responding to the enrichment service")
    print(f"   3. Check if the timeout conditions are being met")
    print(f"   4. Verify the enhanced prompt is being generated correctly")
    print(f"   5. Test direct Ollama API call with the same prompt")
