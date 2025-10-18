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
