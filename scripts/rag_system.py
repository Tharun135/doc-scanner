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
    
    def get_rag_suggestion(feedback_text: str, sentence_context: str, document_type: str = "general", document_content: str = "") -> Dict[str, Any]:
        """
        Get an AI suggestion from the RAG system.
        
        Args:
            feedback_text: The writing issue/feedback
            sentence_context: The original sentence
            document_type: Type of document being processed
            document_content: Full document content for context
            
        Returns:
            Dict containing suggestion, confidence, method, and sources
        """
        try:
            import threading
            import queue
            
            logging.info(f"RAG suggestion request: feedback='{feedback_text}', sentence='{sentence_context}', rag_initialized={rag_system.is_initialized}")
            
            if not rag_system or not rag_system.is_initialized:
                logging.warning("RAG system not initialized, falling back to smart suggestions")
                # Import and use the AI improvement system's smart fallbacks
                try:
                    from app.ai_improvement import AISuggestionEngine
                    ai_engine = AISuggestionEngine()
                    fallback_result = ai_engine.generate_minimal_fallback(feedback_text, sentence_context, 1)
                    logging.info(f"Using smart AI fallback: {fallback_result.get('suggestion', '')[:50]}")
                    return fallback_result
                except Exception as e:
                    logging.error(f"Smart fallback failed: {e}")
                    return {
                        'suggestion': f"Consider revising: {sentence_context}",
                        'confidence': 'medium', 
                        'method': 'smart_fallback',
                        'sources': []
                    }
            
            # Use threading timeout for RAG call
            def rag_call():
                try:
                    logging.info("Calling RAG system...")
                    result = rag_system.get_rag_suggestion(
                        feedback_text=feedback_text,
                        sentence_context=sentence_context,
                        document_type=document_type,
                        document_content=document_content
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
                    'suggestion': f"Consider revising for better clarity: {sentence_context}",
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
                    'suggestion': f"Consider improving clarity: {sentence_context}",
                    'confidence': 'medium',
                    'method': 'smart_fallback',
                    'sources': []
                }
                
        except TimeoutError:
            logging.error("RAG suggestion timed out after 15 seconds")
            return {
                'suggestion': f"Consider revising for better clarity: {sentence_context}",
                'confidence': 'low',
                'method': 'timeout_fallback',
                'sources': []
            }
                
        except Exception as e:
            logging.error(f"RAG suggestion error: {e}")
            return {
                'suggestion': f"Review for improvement: {sentence_context}",
                'confidence': 'low',
                'method': 'error_fallback',
                'sources': []
            }
    
    logging.info("RAG system interface loaded successfully")
    
except ImportError as e:
    RAG_SYSTEM_AVAILABLE = False
    logging.warning(f"RAG system not available: {e}")
    
    def get_rag_suggestion(feedback_text: str, sentence_context: str, document_type: str = "general", document_content: str = "") -> Dict[str, Any]:
        """Fallback function when RAG is not available"""
        return {
            'suggestion': f"Consider revising for better clarity: {sentence_context}",
            'confidence': 'low',
            'method': 'fallback_unavailable',
            'sources': []
        }
