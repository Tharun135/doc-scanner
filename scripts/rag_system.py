"""
RAG System Interface for DocScanner AI
Provides the get_rag_suggestion function expected by the AI improvement system.
"""

import logging
from typing import Dict, List, Optional, Any

# Import the actual RAG implementation
try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    RAG_SYSTEM_AVAILABLE = True
    
    # Initialize the RAG system
    rag_system = DocScannerOllamaRAG()
    logging.info(f"RAG system initialized. Status: {rag_system.is_initialized}")
    
    def get_rag_suggestion(issue: str, sentence: str, writing_goals: List[str] = None, document_type: str = "general") -> Dict[str, Any]:
        """
        Get an AI suggestion from the RAG system.
        
        Args:
            issue: The writing issue/feedback
            sentence: The original sentence
            writing_goals: List of writing goals (e.g., ['clarity', 'conciseness'])
            document_type: Type of document being processed
            
        Returns:
            Dict containing suggestion, confidence, method, and sources
        """
        try:
            import threading
            import queue
            
            logging.info(f"RAG suggestion request: issue='{issue}', sentence='{sentence}', rag_initialized={rag_system.is_initialized}")
            
            if not rag_system or not rag_system.is_initialized:
                logging.warning("RAG system not initialized, falling back to smart suggestions")
                return {
                    'suggestion': f"Consider revising: {sentence}",
                    'confidence': 'medium', 
                    'method': 'smart_fallback',
                    'sources': []
                }
            
            # Use threading timeout for RAG call
            def rag_call():
                try:
                    logging.info("Calling RAG system...")
                    result = rag_system.get_rag_suggestion(
                        feedback_text=issue,
                        sentence_context=sentence,
                        document_type=document_type
                    )
                    return result
                except Exception as e:
                    logging.error(f"RAG call failed: {e}")
                    return None
            
            result_queue = queue.Queue()
            
            def worker():
                result = rag_call()
                result_queue.put(result)
            
            # Start RAG call in separate thread with timeout
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            
            try:
                result = result_queue.get(timeout=15)  # 15 second timeout
                logging.info("RAG system call completed")
            except queue.Empty:
                logging.error("RAG suggestion timed out after 15 seconds")
                return {
                    'suggestion': f"Consider revising for better clarity: {sentence}",
                    'confidence': 'low',
                    'method': 'timeout_fallback',
                    'sources': []
                }
            
            if result and result.get('suggestion'):
                return {
                    'suggestion': result['suggestion'],
                    'confidence': result.get('confidence', 'medium'),
                    'method': 'ollama_rag',
                    'sources': result.get('sources', [])
                }
            else:
                # Fallback if RAG doesn't return a valid response
                logging.warning("RAG returned no valid result")
                return {
                    'suggestion': f"Consider improving clarity: {sentence}",
                    'confidence': 'medium',
                    'method': 'smart_fallback',
                    'sources': []
                }
                
        except TimeoutError:
            signal.alarm(0)  # Cancel timeout
            logging.error("RAG suggestion timed out after 15 seconds")
            return {
                'suggestion': f"Consider revising for better clarity: {sentence}",
                'confidence': 'low',
                'method': 'timeout_fallback',
                'sources': []
            }
                
        except TimeoutError:
            signal.alarm(0)  # Cancel timeout
            logging.error("RAG suggestion timed out after 15 seconds")
            return {
                'suggestion': f"Consider revising for better clarity: {sentence}",
                'confidence': 'low',
                'method': 'timeout_fallback',
                'sources': []
            }
                
        except Exception as e:
            logging.error(f"RAG suggestion error: {e}")
            return {
                'suggestion': f"Review for improvement: {sentence}",
                'confidence': 'low',
                'method': 'error_fallback',
                'sources': []
            }
    
    logging.info("RAG system interface loaded successfully")
    
except ImportError as e:
    RAG_SYSTEM_AVAILABLE = False
    logging.warning(f"RAG system not available: {e}")
    
    def get_rag_suggestion(issue: str, sentence: str, writing_goals: List[str] = None, document_type: str = "general") -> Dict[str, Any]:
        """Fallback function when RAG is not available"""
        return {
            'suggestion': f"Consider revising for better clarity: {sentence}",
            'confidence': 'low',
            'method': 'fallback_unavailable',
            'sources': []
        }
