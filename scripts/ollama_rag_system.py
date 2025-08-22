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

# Ollama + LlamaIndex + ChromaDB imports
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document, Settings
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    import chromadb
    OLLAMA_AVAILABLE = True
    logging.info("Ollama RAG dependencies loaded successfully")
except ImportError as e:
    OLLAMA_AVAILABLE = False
    logging.warning(f"Ollama RAG dependencies not available: {e}")
    logging.info("Install with: pip install llama-index-core llama-index-llms-ollama llama-index-vector-stores-chroma chromadb")

logger = logging.getLogger(__name__)

class OllamaRAGSystem:
    """
    Local RAG system using Ollama LLM + ChromaDB + LlamaIndex
    Provides the same interface as the previous Google Gemini system.
    """
    
    def __init__(self, model="phi3:mini", embed_model="mxbai-embed-large"):
        self.model = model
        self.embed_model = embed_model
        self.llm = None
        self.embeddings = None
        self.chroma_client = None
        self.collection = None
        self.vector_store = None
        self.index = None
        self.query_engine = None
        self.is_initialized = False
        
        if OLLAMA_AVAILABLE:
            self._initialize_ollama()
        else:
            logger.warning("Ollama RAG system disabled - dependencies not installed")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM and embeddings."""
        try:
            # Initialize Ollama LLM
            self.llm = Ollama(
                model=self.model,
                request_timeout=60.0,
                temperature=0.1
            )
            
            # For embeddings, try different models in order of preference
            embedding_models = [
                "mxbai-embed-large",  
                "nomic-embed-text",
                "all-minilm",
                self.model  # Fall back to main model for embeddings
            ]
            
            self.embeddings = None
            for embed_model in embedding_models:
                try:
                    self.embeddings = OllamaEmbedding(
                        model_name=embed_model,
                        base_url="http://localhost:11434",
                        ollama_additional_kwargs={"mirostat": 0}
                    )
                    logger.info(f"Using embedding model: {embed_model}")
                    break
                except Exception as e:
                    logger.warning(f"Embedding model {embed_model} not available: {e}")
                    continue
            
            # If no embedding models work, use the LLM for embeddings
            if self.embeddings is None:
                logger.warning("No embedding models available, using LLM for embeddings")
                # Use a simple embedding strategy with the main model
                self.embeddings = OllamaEmbedding(
                    model_name=self.model,
                    base_url="http://localhost:11434"
                )
            
            # Set global settings for LlamaIndex
            Settings.llm = self.llm
            Settings.embed_model = self.embeddings
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.Client()
            
            # Get or create collection for DocScanner rules
            try:
                self.collection = self.chroma_client.get_collection("docscanner_rules")
                logger.info("Using existing DocScanner rules collection")
            except Exception:
                self.collection = self.chroma_client.create_collection("docscanner_rules")
                logger.info("Created new DocScanner rules collection")
            
            # Create ChromaDB vector store
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)
            
            # Create index from vector store
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                response_mode="compact"
            )
            
            self.is_initialized = True
            logger.info(f"Ollama RAG system initialized with model: {self.model}")
            
            # Load writing rules into vector store
            self._load_writing_rules()
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama RAG system: {e}")
            logger.info("Make sure Ollama is running: 'ollama serve'")
            logger.info(f"And model is downloaded: 'ollama pull {self.model}'")
            self.is_initialized = False
    
    def _load_writing_rules(self):
        """Load DocScanner writing rules into the vector database."""
        try:
            # Define writing rules as documents
            rules_content = [
                {
                    "title": "Passive Voice Rule",
                    "content": "Convert passive voice to active voice for clearer communication. Example: Change 'The report was written by John' to 'John wrote the report'. This makes text more direct and engaging.",
                    "category": "voice",
                    "examples": ["was written -> wrote", "is being developed -> we are developing"]
                },
                {
                    "title": "Long Sentences Rule", 
                    "content": "Break long sentences into shorter, clearer ones. Aim for 15-20 words per sentence for better readability. Use conjunctions and split complex ideas.",
                    "category": "readability",
                    "examples": ["Split at conjunctions", "Use bullet points for lists", "One idea per sentence"]
                },
                {
                    "title": "Modal Verbs Rule",
                    "content": "Replace vague modal verbs (might, could, should) with more precise language. Use definitive statements when possible.",
                    "category": "clarity", 
                    "examples": ["might -> will", "could -> can", "should -> must"]
                },
                {
                    "title": "Weak Verbs Rule",
                    "content": "Replace weak verbs (is, are, have) with strong action verbs. This creates more dynamic and engaging text.",
                    "category": "engagement",
                    "examples": ["is responsible for -> manages", "have the ability -> can", "are capable of -> can"]
                },
                {
                    "title": "Technical Writing Style",
                    "content": "Use clear, concise language for technical documentation. Prefer active voice, present tense, and user-focused instructions.",
                    "category": "style",
                    "examples": ["Click the button", "Enter your password", "Select the option"]
                }
            ]
            
            # Convert rules to LlamaIndex documents
            documents = []
            for rule in rules_content:
                doc_text = f"Title: {rule['title']}\n"
                doc_text += f"Category: {rule['category']}\n"
                doc_text += f"Rule: {rule['content']}\n"
                doc_text += f"Examples: {', '.join(rule['examples'])}"
                
                doc = Document(
                    text=doc_text,
                    metadata={
                        "title": rule['title'],
                        "category": rule['category'],
                        "source": "docscanner_rules"
                    }
                )
                documents.append(doc)
            
            # Add documents to index if we have any
            if documents and self.index:
                # Create a new index with documents
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    vector_store=self.vector_store
                )
                
                # Recreate query engine
                self.query_engine = self.index.as_query_engine(
                    similarity_top_k=3,
                    response_mode="compact"
                )
                
                logger.info(f"Loaded {len(documents)} writing rules into vector store")
            
        except Exception as e:
            logger.warning(f"Could not load writing rules: {e}")
    
    def get_rag_suggestion(self, feedback_text: str, sentence_context: str = "",
                          document_type: str = "general", 
                          document_content: str = "") -> Optional[Dict[str, Any]]:
        """
        Generate RAG suggestion using local Ollama LLM.
        
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
            # Create context-aware query
            query = self._format_rag_query(
                feedback_text, sentence_context, document_type, document_content
            )
            
            # Get response from RAG system
            response = self.query_engine.query(query)
            
            # Extract source information
            sources = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    if hasattr(node, 'metadata'):
                        sources.append({
                            "title": node.metadata.get('title', 'Writing Rule'),
                            "category": node.metadata.get('category', 'general'),
                            "score": getattr(node, 'score', 0.0)
                        })
            
            # Format the response
            suggestion_text = str(response).strip()
            
            return {
                "suggestion": suggestion_text,
                "confidence": self._calculate_confidence(suggestion_text, sources),
                "method": "ollama_rag",
                "sources": sources,
                "model": self.model,
                "context_used": {
                    "document_type": document_type,
                    "has_context": len(sentence_context) > 0,
                    "vector_results": len(sources),
                    "llm": "ollama_local"
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
