#!/usr/bin/env python3
"""
Test direct ollama_rag_direct execution to find the exact issue.
"""

import requests
import json

def test_direct_ollama_call():
    """Test the exact same call that enrichment.py would make."""
    
    print("🔍 TESTING DIRECT OLLAMA_RAG_DIRECT CALL")
    print("=" * 45)
    
    # Simulate the exact same scenario from debug test
    feedback_text = "passive voice detected by rule"
    sentence_context = "The file was saved by the user."
    
    print(f"📝 Test scenario:")
    print(f"   Feedback: '{feedback_text}'")
    print(f"   Sentence: '{sentence_context}'")
    print(f"   Timeout: 8 seconds (quick)")
    
    try:
        # Test ChromaDB connection first
        print(f"\n🔄 Testing ChromaDB connection...")
        from app.services.enrichment import _get_collection, _cached_vector_query
        
        col = _get_collection()
        if not col:
            print(f"❌ ChromaDB collection not available!")
            return
        
        print(f"✅ ChromaDB collection available")
        
        # Test vector query
        print(f"\n🔍 Testing vector query...")
        query_results = _cached_vector_query(f"{feedback_text} {sentence_context}", n_results=3)
        
        if not query_results:
            print(f"❌ No query results!")
            return
            
        if not query_results.get('documents') or not query_results['documents'][0]:
            print(f"❌ Empty query results!")
            return
            
        print(f"✅ Got {len(query_results['documents'][0])} results")
        
        # Build the same prompt as enrichment.py
        print(f"\n📝 Building enhanced prompt...")
        contexts = []
        sources = []
        
        for i, (doc, meta) in enumerate(zip(
            query_results['documents'][0][:2],
            query_results['metadatas'][0][:2] if query_results.get('metadatas') else [{}]*2
        )):
            rule_id = meta.get('rule_id', f'rule_{i+1}')
            title = meta.get('title', 'Writing Rule')
            contexts.append(f"Rule {i+1} ({rule_id}): {title}\n{doc[:400]}")
            sources.append({
                "rule_id": rule_id,
                "title": title,
                "similarity": 0.85 - (i * 0.1)
            })
        
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

        print(f"✅ Prompt built ({len(enhanced_prompt)} chars)")
        print(f"   Context sources: {len(sources)}")
        
        # Test Ollama connection
        print(f"\n🔄 Testing Ollama connection...")
        test_response = requests.get('http://localhost:11434/api/version', timeout=2)
        if test_response.status_code != 200:
            print(f"❌ Ollama not responding: {test_response.status_code}")
            return
            
        print(f"✅ Ollama responding: {test_response.json()}")
        
        # Make the actual call
        print(f"\n🚀 Making actual Ollama API call...")
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
        }, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            print(f"✅ SUCCESS! Ollama responded:")
            print(f"   Status: {response.status_code}")
            print(f"   Response length: {len(ai_response)}")
            print(f"   Response: '{ai_response[:200]}...'")
            
            if len(ai_response) > 20:
                print(f"✅ Response meets length requirement (>20 chars)")
                print(f"\n🎯 THIS SHOULD WORK IN PRODUCTION!")
            else:
                print(f"❌ Response too short: {len(ai_response)} chars")
                
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_ollama_call()
    
    print(f"\n💡 If this test succeeds but the enrichment service fails:")
    print(f"   1. The Flask app might have different imports/environment")
    print(f"   2. The collection might not be available in the Flask context")
    print(f"   3. There might be a bug in the conditional logic")
    print(f"   4. Logger might be hiding the real error")
