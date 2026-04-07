"""
Enrichment service for providing AI-powered writing suggestions.
Uses enhanced RAG integration for improved accuracy.
"""

import logging
import sys
import os

logger = logging.getLogger(__name__)

def enrich_issue_with_solution(issue):
    """
    Enhanced enrichment function that uses the comprehensive rule engine
    and enhanced RAG system for improved AI writing suggestions.
    """
    try:
        # Add enhanced_rag directory to Python path
        enhanced_rag_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "enhanced_rag")
        if enhanced_rag_path not in sys.path:
            sys.path.append(enhanced_rag_path)
        
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

def enrich_issues_with_rag(issues):
    """
    Enrich a list of issues with RAG suggestions.
    This is used by the rule-based system to get AI help.
    """
    if not issues:
        return []
    
    enriched_issues = []
    for issue in issues:
        # If it's just a string, convert to dict
        if isinstance(issue, str):
            issue = {"message": issue, "context": ""}
            
        enriched = enrich_issue_with_solution(issue)
        enriched_issues.append(enriched)
        
    return enriched_issues

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
