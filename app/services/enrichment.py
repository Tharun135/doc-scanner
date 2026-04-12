"""
Enrichment service for providing AI-powered writing suggestions.
Uses enhanced RAG integration for improved accuracy.
"""

import logging
import sys
import os
import concurrent.futures
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try to import skip logic
try:
    from app.rules.rag_rule_helper import should_skip_ai
except ImportError:
    try:
        from ..rules.rag_rule_helper import should_skip_ai
    except ImportError:
        def should_skip_ai(): return False

def enrich_issue_with_solution(issue):
    """
    Enhanced enrichment function that uses the comprehensive rule engine
    and enhanced RAG system for improved AI writing suggestions.
    """
    try:
        # Add tools/ directory to Python path (this is where enhanced_rag_integration.py lives)
        tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)
        
        # Import enhanced system
        from enhanced_rag_integration import enhanced_enrich_issue_with_solution
        
        # Use enhanced system for better accuracy
        result = enhanced_enrich_issue_with_solution(issue)
        
        logger.info(f"[ENRICH] Enhanced system result: {result.get('method', 'unknown')}")
        return result
        
    except ImportError as e:
        logger.warning(f"[ENRICH] Enhanced system not available: {e}. Using basic fallback.")
        
        # Basic fallback for when enhanced system is not available
        issue["solution_text"] = f"Review and improve this text to address: {issue.get('message', 'writing issue')}"
        issue["proposed_rewrite"] = issue.get("context", "")  # Use original text as fallback
        issue["sources"] = []
        issue["method"] = "basic_fallback"
        
        return issue
        
    except Exception as e:
        logger.error(f"[ENRICH] Enhanced system error: {e}. Using basic fallback.")
        
        # Error fallback
        issue["solution_text"] = f"Review and improve this text to address: {issue.get('message', 'writing issue')}"
        issue["proposed_rewrite"] = issue.get("context", "")
        issue["sources"] = []
        issue["method"] = "error_fallback"
        
        return issue

def enrich_issues_with_rag(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich a list of issues with RAG suggestions using parallel processing.
    Groups issues by sentence to minimize AI calls and deduplicate work.
    """
    if not issues:
        return []
        
    logger.info(f"[ENRICH] Starting enrichment for {len(issues)} raw issues")
    
    # --- PHASE 1: SENTENCE-LEVEL GROUPING ---
    # Map unique_sentence -> list of issues for that sentence
    sentence_map = {}
    
    for i, issue in enumerate(issues):
        if isinstance(issue, str):
            issue = {"message": issue, "context": ""}
            issues[i] = issue
            
        ctx = issue.get("context", "").strip()
        if not ctx: continue
        
        if ctx not in sentence_map:
            sentence_map[ctx] = []
        sentence_map[ctx].append(issue)
        
    unique_sentences = list(sentence_map.keys())
    logger.info(f"[ENRICH] Grouped {len(issues)} issues into {len(unique_sentences)} unique sentences")
    
    # --- PHASE 2: LAZY LOADING CHECK ---
    # We no longer return placeholders here. If AI is skipped, just return the issues as-is.
    if should_skip_ai():
        logger.info(f"[ENRICH] ⚡ Lazy Mode Active: Skipping batch enrichment for {len(unique_sentences)} segments")
        return issues

    # --- PHASE 3: PARALLEL ENRICHMENT BY SENTENCE ---
    # We use a smaller pool (5) to avoid thrashing local Ollama
    max_workers = min(len(unique_sentences), 5)
    sentence_results = {}
    
    if max_workers > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Task: Enrich a sentence which may contain multiple issues
            def process_sentence(ctx):
                sentence_issues = sentence_map[ctx]
                # If there are multiple issues, we pass them as a list to the enhanced system
                # The enhanced system will handle multiple feedback strings in one prompt
                if len(sentence_issues) > 1:
                    # Combine messages
                    combined_msg = " | ".join(set(iss.get("message", "") for iss in sentence_issues))
                    root_issue = sentence_issues[0].copy()
                    root_issue["message"] = combined_msg
                    # Mark that it has multiple issues for the prompt generator
                    root_issue["multiple_issues"] = [iss.get("message", "") for iss in sentence_issues]
                    return enrich_issue_with_solution(root_issue)
                else:
                    return enrich_issue_with_solution(sentence_issues[0])

            # Submit unique sentences
            future_to_ctx = {executor.submit(process_sentence, ctx): ctx for ctx in unique_sentences}
            
            for future in concurrent.futures.as_completed(future_to_ctx):
                ctx = future_to_ctx[future]
                try:
                    sentence_results[ctx] = future.result()
                except Exception as e:
                    logger.error(f"[ENRICH] Failed to process sentence '{ctx[:30]}...': {e}")
                    # Fallback: create basic result
                    sentence_results[ctx] = sentence_map[ctx][0]

    # --- PHASE 3: RECONSTRUCTION ---
    # Map back to the original issues list
    final_results = []
    for issue in issues:
        ctx = issue.get("context", "").strip()
        if ctx in sentence_results:
            # We want each issue to have the solution for its sentence
            # Even if it was part of a group, the proposed_rewrite is for the sentence
            res = sentence_results[ctx].copy()
            # Restore the original message so the UI knows which rule this result belongs to
            res["message"] = issue.get("message", "")
            final_results.append(res)
        else:
            final_results.append(issue)
            
    return final_results

def ingest_document_to_rag(text, doc_id, product="docscanner", version="1.0"):
    """
    Ingest a document into the RAG system for future retrieval.
    """
    try:
        # Add tools folder to path
        tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)
            
        from enhanced_rag_integration import get_enhanced_rag_integration
        
        integration = get_enhanced_rag_integration()
        chunk_count = integration.ingest_document(
            document_text=text,
            source_doc_id=doc_id,
            product=product,
            version=version
        )
        
        logger.info(f"[ENRICH] Ingested {doc_id}: {chunk_count} chunks created")
        return chunk_count
        
    except Exception as e:
        logger.error(f"[ENRICH] Ingestion failed for {doc_id}: {e}")
        return 0

def ingest_correction(original, corrected, issue_type, product="docscanner", version="1.0"):
    """
    Save a user-accepted correction back into the Knowledge Base as a 'Golden Pair'.
    This enables the system to learn from its best suggestions.
    """
    try:
        # Add tools folder to path
        tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)
            
        from enhanced_rag_integration import get_enhanced_rag_integration
        
        # Format the correction as a rule entry
        rule_text = f"Context: {issue_type}\nOriginal: {original}\nCorrected: {corrected}"
        
        integration = get_enhanced_rag_integration()
        chunk_count = integration.ingest_document(
            document_text=rule_text,
            source_doc_id=f"learned_{hash(original)}",
            product=product,
            version=version,
            metadata={"type": "learned_rule", "issue": issue_type}
        )
        
        logger.info(f"[LEARN] Saved new golden pair for {issue_type}")
        return True
    except Exception as e:
        logger.error(f"[LEARN] Learning failed: {e}")
        return False

# Test function when run directly
if __name__ == "__main__":
    test_issue = {
        'message': 'Consider using sentence case for this text',
        'context': 'it is in ISO 8601 format.',
        'issue_type': 'style'
    }
    
    result = enrich_issue_with_solution(test_issue)
    print('Method:', result.get('method'))
    print('Original:', test_issue['context'])
    print('Rewrite:', result.get('proposed_rewrite'))
    print('Guidance:', result.get('solution_text', '')[:100])
