"""
Ollama RAG System - Local LLM + ChromaDB + LlamaIndex
Replaces the Google Gemini + LangChain setup with fully local components.
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Ollama + ChromaDB imports (removed LlamaIndex due to memory issues)
try:
    import chromadb
    import requests
    OLLAMA_AVAILABLE = True
    logging.info("Ollama RAG dependencies loaded successfully")
except ImportError as e:
    OLLAMA_AVAILABLE = False
    logging.warning(f"Ollama RAG dependencies not available: {e}")
    logging.info("Install with: pip install chromadb requests")

logger = logging.getLogger(__name__)

class OllamaRAGSystem:
    """
    Local RAG system using Ollama LLM + ChromaDB + LlamaIndex
    Provides the same interface as the previous Google Gemini system.
    """
    
    def __init__(self, model="phi3:mini", embed_model="mxbai-embed-large"):
        self.model = model
        self.embed_model = embed_model
        self.chroma_client = None
        self.collection = None
        self.is_initialized = False
        
        if OLLAMA_AVAILABLE:
            self._initialize_ollama()
        else:
            logger.warning("Ollama RAG system disabled - dependencies not installed")
    
    def _initialize_ollama(self):
        """Initialize Ollama connection and ChromaDB."""
        try:
            # Test Ollama connection with direct API
            import requests
            test_response = requests.post('http://localhost:11434/api/generate', 
                                       json={'model': self.model, 'prompt': 'test', 'stream': False},
                                       timeout=30)
            
            if test_response.status_code != 200:
                logger.error(f"Ollama not responding properly: {test_response.text}")
                self.is_initialized = False
                return
            
            # Initialize ChromaDB with persistent storage
            chroma_path = os.path.expanduser("./chroma_db")  # Use the database we populated
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            
            # Get existing collection for DocScanner solutions
            try:
                self.collection = self.chroma_client.get_collection("docscanner_solutions")
                logger.info("Using existing DocScanner solutions collection")
                
                # Verify collection has data
                count = self.collection.count()
                if count == 0:
                    logger.warning("DocScanner solutions collection is empty")
                else:
                    logger.info(f"Collection has {count} documents")
                    
            except Exception:
                logger.error("DocScanner solutions collection not found - run ingest_docscanner_solutions.py first")
                self.is_initialized = False
                return
            
            self.is_initialized = True
            logger.info(f"Ollama RAG system initialized with model: {self.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama RAG system: {e}")
            logger.info("Make sure Ollama is running: 'ollama serve'")
            logger.info(f"And model is downloaded: 'ollama pull {self.model}'")
            self.is_initialized = False
    
    def get_rag_suggestion(self, feedback_text: str, sentence_context: str = "",
                          document_type: str = "general", 
                          document_content: str = "") -> Optional[Dict[str, Any]]:
        """
        Generate RAG suggestion using direct Ollama API + ChromaDB.
        
        Args:
            feedback_text: Description of the writing issue
            sentence_context: The problematic sentence
            document_type: Type of document (technical, general, etc.)
            document_content: Full document content for context
            
        Returns:
            Dict with suggestion, confidence, method, and sources
        """
        
        if not self.is_initialized:
            logger.warning("Ollama RAG system not initialized")
            return None
            
        try:
            # Use direct Ollama API instead of LlamaIndex to avoid memory issues
            import requests
            
            # Query ChromaDB for relevant context
            query_text = f"{feedback_text} {sentence_context}"
            results = self.collection.query(
                query_texts=[query_text],
                n_results=3
            )
            
            if not results['documents'][0]:
                logger.warning("No relevant documents found in ChromaDB")
                return None
            
            # Build context from retrieved documents
            context = "\n\n".join(results['documents'][0])
            sources = []
            
            # Extract metadata for sources
            if results.get('metadatas') and results['metadatas'][0]:
                for i, metadata in enumerate(results['metadatas'][0]):
                    sources.append({
                        "title": metadata.get('title', f'Rule {i+1}'),
                        "category": metadata.get('category', 'general'),
                        "score": results['distances'][0][i] if results.get('distances') else 0.0
                    })
            
            # Create RAG prompt
            rag_prompt = f"""You are a professional writing improvement assistant. Based on the following writing guidance, provide a specific suggestion for improving the given sentence.

WRITING GUIDANCE:
{context[:1000]}

USER ISSUE: {feedback_text}
SENTENCE: "{sentence_context}"
DOCUMENT TYPE: {document_type}

Provide a clear, actionable improvement suggestion in 1-2 sentences:"""

            # Send to Ollama using direct API
            ollama_url = "http://localhost:11434/api/generate"
            response = requests.post(ollama_url, json={
                'model': self.model,
                'prompt': rag_prompt,
                'stream': False
            })
            
            if response.status_code != 200:
                logger.error(f"Ollama API failed: {response.text}")
                return None
            
            result = response.json()
            suggestion_text = result['response'].strip()
            
            return {
                "suggestion": suggestion_text,
                "confidence": self._calculate_confidence(suggestion_text, sources),
                "method": "ollama_rag_direct",
                "sources": sources,
                "model": self.model,
                "context_used": {
                    "document_type": document_type,
                    "has_context": len(sentence_context) > 0,
                    "vector_results": len(sources),
                    "llm": "ollama_direct_api"
                }
            }
            
        except Exception as e:
            logger.error(f"Ollama RAG suggestion failed: {e}")
            return None
    
    def _format_rag_query(self, feedback_text: str, sentence_context: str, 
                         document_type: str, document_content: str) -> str:
        """Format the query for RAG retrieval and generation."""
        
        query = f"""You are an expert technical writing assistant. 

WRITING ISSUE: {feedback_text}

ORIGINAL SENTENCE: "{sentence_context}"

DOCUMENT TYPE: {document_type}

Please provide a complete rewrite of the sentence that fixes the identified issue. 

Requirements:
- Rewrite the ENTIRE sentence, not just the problematic part
- Make it clear, direct, and appropriate for {document_type} writing  
- Use active voice when possible
- Ensure the meaning is preserved

Format your response as:
REWRITE: [Complete sentence rewrite]
EXPLANATION: [Brief explanation of what was improved]
"""
        
        return query
    
    def _calculate_confidence(self, suggestion: str, sources: List[Dict]) -> str:
        """Calculate confidence level based on response quality and sources."""
        
        if not suggestion or len(suggestion.strip()) < 10:
            return "low"
        
        if len(sources) >= 2:
            return "high"
        elif len(sources) == 1:
            return "medium"
        else:
            return "medium"  # Still decent with Ollama reasoning
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Ollama connection and return status."""
        
        if not OLLAMA_AVAILABLE:
            return {
                "status": "failed",
                "reason": "Dependencies not installed",
                "fix": "pip install llama-index-core llama-index-llms-ollama llama-index-vector-stores-chroma chromadb"
            }
        
        if not self.is_initialized:
            return {
                "status": "failed", 
                "reason": "Not initialized",
                "fix": "Check if Ollama is running and model is available"
            }
        
        try:
            # Test simple query
            test_response = self.query_engine.query("What is good technical writing?")
            
            return {
                "status": "success",
                "model": self.model,
                "embed_model": self.embed_model,
                "response_length": len(str(test_response)),
                "collection_count": self.collection.count() if self.collection else 0
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "reason": str(e),
                "fix": "Ensure Ollama server is running: 'ollama serve'"
            }

# Global instance
_ollama_rag_system = None

def get_rag_suggestion(feedback_text: str, sentence_context: str = "",
                      document_type: str = "general", 
                      document_content: str = "") -> Optional[Dict[str, Any]]:
    """
    Global function to get RAG suggestion - maintains compatibility with existing code.
    """
    global _ollama_rag_system
    
    if _ollama_rag_system is None:
        _ollama_rag_system = OllamaRAGSystem()
    
    return _ollama_rag_system.get_rag_suggestion(
        feedback_text, sentence_context, document_type, document_content
    )

def test_ollama_rag():
    """Test function for the Ollama RAG system."""
    
    print("🧪 Testing Ollama RAG System")
    print("=" * 40)
    
    system = OllamaRAGSystem()
    
    # Test connection
    status = system.test_connection()
    print(f"Connection Status: {status}")
    
    if status["status"] == "success":
        # Test actual suggestion
        test_result = system.get_rag_suggestion(
            feedback_text="Passive voice detected: 'was written' - convert to active voice",
            sentence_context="The document was written by John yesterday.",
            document_type="technical"
        )
        
        if test_result:
            print(f"✅ RAG Test Success!")
            print(f"Method: {test_result['method']}")
            print(f"Confidence: {test_result['confidence']}")
            print(f"Model: {test_result['model']}")
            print(f"Sources: {len(test_result['sources'])}")
            print(f"Suggestion: {test_result['suggestion'][:200]}...")
        else:
            print("❌ RAG Test Failed - No suggestion returned")
    else:
        print(f"❌ Connection failed: {status['reason']}")
        print(f"💡 Fix: {status.get('fix', 'Check Ollama installation')}")

if __name__ == "__main__":
    test_ollama_rag()
