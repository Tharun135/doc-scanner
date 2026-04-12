"""
Contextual Validator for DocScanner
This module implements "Stage B: Contextual Accuracy" using RAG.
It checks sentences against a "Gold Standard" knowledge base to detect 
technical inaccuracies, terminology drifts, and non-standard naming.
"""

import re
import logging
import requests
from typing import List, Dict, Any, Optional
from tools.enhanced_rag_integration import query_knowledge_base

logger = logging.getLogger(__name__)

# Lazy-load spaCy for entity extraction
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            # Load with NER for entity extraction
            _nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy not available for contextual validator: {e}")
            _nlp = False
    return _nlp if _nlp is not False else None

def extract_keywords(sentence: str) -> List[str]:
    """Extract key technical terms and entities for RAG retrieval."""
    nlp = _get_nlp()
    if not nlp:
        # Simple regex fallback (proper nouns and technical-looking words)
        return re.findall(r'\b[A-Z][A-Za-z0-9\-]{2,}\b', sentence)
    
    doc = nlp(sentence)
    keywords = []
    
    # Add named entities (ORGs, PRODUCTs, GPEs)
    for ent in doc.ents:
        keywords.append(ent.text)
    
    # Add noun chunks (Technical terms like "Industrial Edge Device")
    for chunk in doc.noun_chunks:
        # Only keep chunks with technical weight (more than 1 word or specific patterns)
        if len(chunk.text.split()) > 1 or re.search(r'[A-Z0-9]', chunk.text):
            keywords.append(chunk.text)
            
    return list(set(keywords))

def check_sentence_accuracy(sentence: str, context_chunks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Compare a sentence against retrieved context using Ollama."""
    if not context_chunks:
        return None
    
    # Construct context string
    reference_text = "\n---\n".join([f"Source: {c['metadata'].get('source', 'Knowledge Base')}\nContent: {c['content']}" for c in context_chunks])
    
    prompt = f"""You are a Technical Documentation Auditor. 
Compare the following SENTENCE against the provided REFERENCE CONTEXT.

SENTENCE: "{sentence}"

REFERENCE CONTEXT:
{reference_text}

Check for:
1. Technical Contradictions: Does the sentence state something technically incorrect according to the reference?
2. Terminology Drift: Does the sentence use a term that is named differently in the reference (e.g., using "DCS" when reference uses "DCS-Pro")?
3. Invention Risk: Does the sentence mention a product or feature that doesn't exist in the reference?

If you find an issue, return a JSON object with:
"issue_type": "Technical Drift" or "Contradiction" or "Terminology Violation"
"explanation": Clear explanation of why it's wrong based on the context.
"suggested_fix": A rewritten version of the sentence that is contextually accurate.

If the sentence is accurate and consistent, return "STRICTLY_ACCURATE".

RESPONSE:"""

    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'phi3:mini',
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0,
                'num_predict': 300
            }
        }, timeout=20)
        
        if response.status_code == 200:
            result_text = response.json().get('response', '').strip()
            
            if "STRICTLY_ACCURATE" in result_text:
                return None
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                import json
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Simple parsing fallback
            if "issue_type" in result_text.lower():
                return {
                    "issue_type": "Contextual Accuracy",
                    "explanation": result_text[:200] + "...",
                    "suggested_fix": sentence # Fallback
                }
                
    except Exception as e:
        logger.error(f"Ollama comparison failed: {e}")
        
    return None

def validate_contextual_accuracy(text: str) -> List[Dict[str, Any]]:
    """
    Review document text for semantic and contextual accuracy using RAG.
    """
    issues = []
    
    # Split into sentences (simple split for now to avoid multiple spaCy passes)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15] # Skip very short snippets
    
    # Process only a subset or significant sentences to avoid excessive AI latency
    # In a full production system, we'd do this in background
    for sent in sentences[:15]: # Limit to first 15 sentences for the review
        keywords = extract_keywords(sent)
        if not keywords:
            continue
            
        # Query knowledge base
        query_text = " ".join(keywords)
        context = query_knowledge_base(query_text, n_results=3)
        
        if context:
            error = check_sentence_accuracy(sent, context)
            if error:
                issues.append({
                    "sentence": sent,
                    "problem": f"{error.get('issue_type', 'Contextual Accuracy')}: {error.get('explanation', '')}",
                    "suggested_revision": error.get('suggested_fix', sent)
                })
                
    return issues
