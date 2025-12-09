#!/usr/bin/env python3
"""
Create a simple direct Ollama RAG integration for the enrichment service.
This will ensure rule-based issues get ollama_rag_direct responses.
"""

import chromadb
from chromadb.config import Settings
import requests
import json
import logging

logger = logging.getLogger(__name__)

def get_ollama_rag_direct_suggestion(feedback_text: str, sentence_context: str) -> dict:
    """
    Direct ollama_rag_direct implementation for enrichment service.
    Bypasses complex integrations and directly calls Ollama with RAG context.
    """
    
    try:
        # Get ChromaDB context
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_collection(name="docscanner_solutions")
        
        # Query for relevant RAG context
        query_text = f"{feedback_text} {sentence_context}"
        results = collection.query(
            query_texts=[query_text],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'][0]:
            logger.warning("No ChromaDB results for ollama_rag_direct")
            return None
        
        # Format RAG context
        context_docs = results['documents'][0]
        context_metas = results['metadatas'][0]
        
        rag_context = ""
        sources = []
        
        for i, (doc, meta) in enumerate(zip(context_docs, context_metas)):
            rule_id = meta.get('rule_id', f'rule_{i}')
            title = meta.get('title', 'Writing Rule')
            rag_context += f"\nRule {i+1} ({rule_id}): {title}\n{doc}\n"
            
            sources.append({
                "rule_id": rule_id,
                "title": title,
                "similarity": 1.0 - results['distances'][0][i] if results.get('distances') else 0.8
            })
        
        # Create Ollama prompt with RAG context
        ollama_prompt = f"""You are an expert technical writing assistant with access to comprehensive writing rules.

WRITING ISSUE: {feedback_text}
ORIGINAL SENTENCE: "{sentence_context}"

RELEVANT WRITING RULES:
{rag_context}

Based on the above rules, provide specific guidance to fix this writing issue. Your response should:
1. Identify the specific problem
2. Explain why it matters
3. Provide concrete improvement suggestions

Be direct and actionable. Focus on the specific issue identified."""

        # Call Ollama API directly
        ollama_url = "http://localhost:11434/api/generate"
        response = requests.post(ollama_url, json={
            'model': 'phi3:mini',
            'prompt': ollama_prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'top_p': 0.9,
                'num_predict': 200
            }
        }, timeout=10)  # 10 second timeout for high-quality responses
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get('response', '').strip()
            
            if ai_response and len(ai_response) > 20:  # Ensure we got a substantial response
                logger.info(f"✅ ollama_rag_direct success: {len(ai_response)} chars")
                
                return {
                    "method": "ollama_rag_direct",
                    "ai_answer": ai_response,
                    "suggestion": ai_response,  # Use AI response as suggestion
                    "sources": sources,
                    "confidence": "high",
                    "context_used": {
                        "rag_docs": len(context_docs),
                        "model": "phi3:mini",
                        "method": "direct_ollama_api"
                    }
                }
            else:
                logger.warning(f"ollama_rag_direct returned short response: {ai_response}")
                
        else:
            logger.warning(f"Ollama API error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        logger.warning("ollama_rag_direct timeout - falling back")
    except Exception as e:
        logger.warning(f"ollama_rag_direct failed: {e}")
    
    return None

if __name__ == "__main__":
    # Test the direct ollama RAG function
    print("🧪 Testing Direct Ollama RAG Integration")
    
    test_cases = [
        {
            "feedback": "passive voice detected",
            "sentence": "The configuration was completed by the user."
        },
        {
            "feedback": "unnecessary adverbs",
            "sentence": "You can easily configure the settings."
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Testing: {test['feedback']}")
        print(f"   Sentence: {test['sentence']}")
        
        result = get_ollama_rag_direct_suggestion(test['feedback'], test['sentence'])
        
        if result:
            print(f"   ✅ Method: {result['method']}")
            print(f"   💡 AI Response: {result['ai_answer'][:100]}...")
            print(f"   📚 Sources: {len(result['sources'])} rules")
        else:
            print("   ❌ No result")
