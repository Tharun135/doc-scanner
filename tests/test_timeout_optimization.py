#!/usr/bin/env python3
"""
Test ollama_rag_direct with different timeout values.
"""

import requests
import json
import time

def test_ollama_with_timeouts():
    """Test ollama with different timeout values."""
    
    print("🔍 TESTING OLLAMA_RAG_DIRECT WITH DIFFERENT TIMEOUTS")
    print("=" * 55)
    
    # Test data
    feedback_text = "passive voice detected by rule"
    sentence_context = "The file was saved by the user."
    
    # Import enrichment service functions
    from app.services.enrichment import _get_collection, _cached_vector_query
    
    # Get the context (same as enrichment service)
    col = _get_collection()
    query_results = _cached_vector_query(f"{feedback_text} {sentence_context}", n_results=3)
    
    # Build the same prompt
    contexts = []
    for i, (doc, meta) in enumerate(zip(
        query_results['documents'][0][:2],
        query_results['metadatas'][0][:2] if query_results.get('metadatas') else [{}]*2
    )):
        rule_id = meta.get('rule_id', f'rule_{i+1}')
        title = meta.get('title', 'Writing Rule')
        contexts.append(f"Rule {i+1} ({rule_id}): {title}\n{doc[:400]}")
    
    enhanced_prompt = f"""You are an expert technical writing assistant. Fix this writing issue with specific, actionable guidance.

ISSUE: {feedback_text}
ORIGINAL: "{sentence_context}"

RELEVANT WRITING RULES:
{chr(10).join(contexts)}

TASK: Provide specific guidance to fix this issue. Include:
1. What the problem is
2. Why it matters  
3. Specific improvement suggestion

Response format: Clear, direct guidance in 2-3 sentences."""
    
    # Test different timeout values
    timeouts = [8, 12, 15, 20, 25]
    
    for timeout in timeouts:
        print(f"\n🔄 Testing with {timeout}s timeout...")
        
        try:
            start_time = time.time()
            
            response = requests.post('http://localhost:11434/api/generate', json={
                'model': 'tinyllama:latest',
                'prompt': enhanced_prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'top_p': 0.7,
                    'num_predict': 50,
                    'num_ctx': 1024,
                    'repeat_penalty': 1.0
                }
            }, timeout=timeout)
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '').strip()
                
                print(f"✅ SUCCESS with {timeout}s timeout!")
                print(f"   Actual time: {duration:.2f}s")
                print(f"   Response length: {len(ai_response)}")
                print(f"   Response: '{ai_response[:100]}...'")
                
                if len(ai_response) > 20:
                    print(f"✅ Response meets quality requirement")
                    
                    # This timeout works! Update the enrichment service
                    print(f"\n🎯 SOLUTION FOUND: Use {timeout}s timeout instead of 8s")
                    print(f"   Actual response time: {duration:.2f}s")
                    break
                else:
                    print(f"⚠️ Response too short")
            else:
                print(f"❌ HTTP error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ Still timing out at {timeout}s")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_faster_model():
    """Test with a faster model configuration."""
    
    print(f"\n\n🚀 TESTING ULTRA-FAST CONFIGURATION")
    print("=" * 40)
    
    # Shorter prompt for speed
    simple_prompt = f"""Fix passive voice: "The file was saved by the user."

Guidance: Convert to active voice. Make the subject perform the action directly."""
    
    print(f"📝 Using ultra-short prompt ({len(simple_prompt)} chars)")
    
    try:
        start_time = time.time()
        
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'tinyllama:latest',
            'prompt': simple_prompt,
            'stream': False,
            'options': {
                'temperature': 0.0,      # Completely deterministic
                'top_p': 0.5,           # Very focused
                'num_predict': 30,      # Shorter response
                'num_ctx': 512,         # Smaller context
                'repeat_penalty': 1.0
            }
        }, timeout=8)
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            print(f"✅ ULTRA-FAST SUCCESS!")
            print(f"   Time: {duration:.2f}s (under 8s limit)")
            print(f"   Response: '{ai_response}'")
            
            if len(ai_response) > 10:
                print(f"✅ Quality sufficient for RAG")
                return True
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Still timing out with ultra-fast config")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    # First try standard timeouts
    test_ollama_with_timeouts()
    
    # Then try ultra-fast configuration
    if test_faster_model():
        print(f"\n💡 RECOMMENDATION: Use ultra-fast configuration for production")
    else:
        print(f"\n💡 RECOMMENDATION: Increase timeout to 15-20 seconds")
