"""
Enhanced RAG System for Document Scanner
=========================================

This system transforms detected issues into intelligent queries, searches a knowledge base,
and uses LLM to provide polished, grammar-perfect responses.

Workflow:
1. Issue Detection → Transform into RAG query
2. Query Knowledge Base → Retrieve relevant information
3. LLM Enhancement → Polish response with perfect grammar
4. Return enhanced suggestion to user
"""

import logging
import json
import time
import os
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib

# Import LlamaIndex components
try:
    from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.retrievers import VectorIndexRetriever
    import chromadb
    import requests
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LlamaIndex/ChromaDB dependencies not available: {e}")
    LLAMAINDEX_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedRAGSystem:
    """Complete RAG system that transforms issues into polished responses."""
    
    def __init__(self, model_name: str = "mistral"):
        self.model_name = model_name
        self.rag_available = LLAMAINDEX_AVAILABLE
        self.llm = None
        self.embed_model = None
        self.index = None
        self.query_engine = None
        self.chroma_client = None
        self.vector_store = None
        self.is_initialized = False
        
        # Cache for enhanced responses
        self.response_cache_file = "enhanced_rag_cache.json"
        self.response_cache = self._load_cache()
        
        if self.rag_available:
            self._initialize_rag_system()
        else:
            logger.warning("Enhanced RAG system disabled - dependencies not installed")
    
    def _load_cache(self) -> Dict:
        """Load enhanced response cache."""
        try:
            if os.path.exists(self.response_cache_file):
                with open(self.response_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load enhanced RAG cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save enhanced response cache."""
        try:
            with open(self.response_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.response_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save enhanced RAG cache: {e}")
    
    def _check_ollama_service(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_model_availability(self, model_name: str) -> bool:
        """Check if a specific model is available in Ollama."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"].split(":")[0] for model in models]
                return model_name in available_models
            return False
        except Exception:
            return False
    
    def _initialize_rag_system(self):
        """Initialize the complete RAG system with ChromaDB and Ollama."""
        try:
            logger.info("🚀 Initializing Enhanced RAG System...")
            
            # Check Ollama service
            if not self._check_ollama_service():
                logger.warning("Ollama service not running. Please start: 'ollama serve'")
                return
            
            # Find available model
            if not self._check_model_availability(self.model_name):
                fallback_models = ["mistral", "phi3", "llama2", "tinyllama"]
                for fallback in fallback_models:
                    if self._check_model_availability(fallback):
                        logger.info(f"Using fallback model: {fallback}")
                        self.model_name = fallback
                        break
                else:
                    logger.error("No compatible models found. Please install: ollama pull mistral")
                    return
            
            # Initialize LLM
            self.llm = Ollama(
                model=self.model_name,
                request_timeout=60.0,
                temperature=0.2  # Lower temperature for more consistent responses
            )
            
            # Initialize embedding model
            self.embed_model = OllamaEmbedding(
                model_name=self.model_name,
                base_url="http://localhost:11434",
                ollama_additional_kwargs={"mirostat": 0}
            )
            
            # Configure global settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path="./enhanced_rag_db")
            
            # Create or get collection for writing knowledge
            collection_name = "writing_knowledge"
            try:
                collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"Using existing ChromaDB collection: {collection_name}")
            except:
                collection = self.chroma_client.create_collection(collection_name)
                logger.info(f"Created new ChromaDB collection: {collection_name}")
                self._populate_knowledge_base(collection)
            
            # Create ChromaDB vector store
            self.vector_store = ChromaVectorStore(chroma_collection=collection)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Create or load index
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=storage_context
                )
                logger.info("Loaded existing vector index")
            except:
                # Create new index if none exists
                documents = self._create_knowledge_documents()
                self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=storage_context
                )
                logger.info("Created new vector index")
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                response_mode="tree_summarize"
            )
            
            self.is_initialized = True
            logger.info(f"✅ Enhanced RAG system initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.is_initialized = False
    
    def _populate_knowledge_base(self, collection):
        """Populate ChromaDB with writing knowledge."""
        knowledge_docs = [
            {
                "id": "passive_voice_1",
                "text": "Passive voice improvement: Convert 'was written by' to active voice by making the actor the subject. Example: 'The document was written by John' becomes 'John wrote the document'.",
                "category": "passive_voice"
            },
            {
                "id": "long_sentence_1", 
                "text": "Long sentence improvement: Break sentences over 25 words into shorter ones. Split at coordinating conjunctions and separate dependent clauses.",
                "category": "long_sentences"
            },
            {
                "id": "modifier_1",
                "text": "Unnecessary modifier improvement: Remove weak modifiers like 'very', 'really', 'quite'. Replace with stronger, more specific words. 'Very good' becomes 'excellent'.",
                "category": "modifiers"
            }
        ]
        
        try:
            collection.add(
                documents=[doc["text"] for doc in knowledge_docs],
                metadatas=[{"category": doc["category"]} for doc in knowledge_docs],
                ids=[doc["id"] for doc in knowledge_docs]
            )
            logger.info(f"Populated ChromaDB with {len(knowledge_docs)} knowledge documents")
        except Exception as e:
            logger.error(f"Failed to populate knowledge base: {e}")
    
    def _create_knowledge_documents(self) -> List:
        """Create LlamaIndex documents from knowledge base."""
        if not LLAMAINDEX_AVAILABLE:
            return []
            
        knowledge_content = [
            "Passive voice uses 'to be' verbs with past participles. Convert to active voice by making the actor the subject. Example: 'The report was completed by the team' becomes 'The team completed the report'.",
            "Long sentences reduce readability. Break sentences over 20-25 words into shorter ones. Split at coordinating conjunctions and separate complex ideas.",
            "Unnecessary modifiers like 'very', 'really', 'quite' weaken writing. Remove them or use stronger, more specific words instead."
        ]
        
        documents = []
        for i, content in enumerate(knowledge_content):
            doc = Document(text=content, metadata={"doc_id": f"knowledge_{i}"})
            documents.append(doc)
        
        return documents
    
    def transform_issue_to_query(self, issue_text: str, issue_type: str = "general") -> str:
        """Transform a detected issue into an intelligent RAG query."""
        clean_text = re.sub(r'[^\w\s]', ' ', issue_text).strip()
        
        query_templates = {
            "passive_voice": f"How to convert passive voice to active voice for: {clean_text}",
            "long_sentence": f"How to break down this long sentence: {clean_text}",
            "modifier": f"How to improve weak modifiers in: {clean_text}",
            "unnecessary_modifier": f"How to remove unnecessary modifiers from: {clean_text}",
            "clarity": f"How to make this text clearer: {clean_text}",
            "grammar": f"How to fix grammar issues in: {clean_text}"
        }
        
        # Auto-detect issue type if not provided
        if issue_type == "general":
            issue_lower = issue_text.lower()
            if "passive voice" in issue_lower:
                issue_type = "passive_voice"
            elif "long sentence" in issue_lower:
                issue_type = "long_sentence"
            elif "modifier" in issue_lower:
                issue_type = "modifier"
        
        query = query_templates.get(issue_type, f"How to improve this writing: {clean_text}")
        logger.info(f"Transformed '{issue_type}' to query: {query[:100]}...")
        return query
    
    def search_knowledge(self, query: str) -> str:
        """Search the knowledge base for relevant information."""
        if not self.is_initialized or not self.query_engine:
            logger.warning("RAG system not initialized, cannot search knowledge")
            return ""
        
        try:
            response = self.query_engine.query(query)
            knowledge_text = str(response)
            logger.info(f"Retrieved knowledge: {len(knowledge_text)} characters")
            return knowledge_text
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return ""
    
    def polish_with_llm(self, knowledge: str, original_issue: str, context: str = "") -> str:
        """Use LLM to polish the knowledge into a perfect response."""
        if not self.is_initialized or not self.llm:
            logger.warning("LLM not initialized, cannot polish response")
            return knowledge if knowledge else original_issue
        
        try:
            polish_prompt = f"""You are an expert writing coach. Create a clear, helpful, and grammatically perfect suggestion.

ORIGINAL ISSUE: {original_issue}
KNOWLEDGE: {knowledge}
CONTEXT: {context}

Provide a concise, actionable suggestion that:
1. Is grammatically perfect
2. Explains the issue clearly
3. Gives specific improvement advice
4. Is encouraging and professional

Response:"""
            
            response = self.llm.complete(polish_prompt)
            polished_text = str(response).strip()
            
            # Clean up the response
            polished_text = re.sub(r'\n+', ' ', polished_text)
            polished_text = re.sub(r'\s+', ' ', polished_text)
            
            logger.info(f"LLM polished response: {len(polished_text)} characters")
            return polished_text
            
        except Exception as e:
            logger.error(f"Error polishing with LLM: {e}")
            return knowledge if knowledge else original_issue
    
    def get_enhanced_suggestion(self, issue_text: str, issue_type: str = "general", 
                              context: str = "") -> Dict[str, Any]:
        """Complete RAG workflow: Issue → Query → Knowledge → Polish → Response"""
        start_time = time.time()
        
        # Create cache key
        cache_key = hashlib.md5(f"{issue_text}:{issue_type}:{context}".encode()).hexdigest()
        
        # Check cache first
        if cache_key in self.response_cache:
            logger.info("Retrieved enhanced suggestion from cache")
            return self.response_cache[cache_key]
        
        try:
            # Step 1: Transform issue to query
            query = self.transform_issue_to_query(issue_text, issue_type)
            
            # Step 2: Search knowledge base
            knowledge = self.search_knowledge(query)
            
            # Step 3: Polish with LLM
            polished_response = self.polish_with_llm(knowledge, issue_text, context)
            
            # Create enhanced response
            enhanced_suggestion = {
                "original_issue": issue_text,
                "issue_type": issue_type,
                "query_used": query,
                "knowledge_retrieved": knowledge,
                "enhanced_response": polished_response,
                "method": "enhanced_rag",
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            self.response_cache[cache_key] = enhanced_suggestion
            self._save_cache()
            
            logger.info(f"Generated enhanced suggestion in {enhanced_suggestion['processing_time']:.2f}s")
            return enhanced_suggestion
            
        except Exception as e:
            logger.error(f"Error in enhanced RAG workflow: {e}")
            return {
                "original_issue": issue_text,
                "issue_type": issue_type,
                "enhanced_response": issue_text,
                "method": "enhanced_rag_error",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "rag_available": self.rag_available,
            "is_initialized": self.is_initialized,
            "model_name": self.model_name,
            "cached_responses": len(self.response_cache),
            "ollama_service": self._check_ollama_service() if self.rag_available else False,
            "dependencies": {
                "llamaindex": LLAMAINDEX_AVAILABLE,
                "chromadb": self.chroma_client is not None,
                "ollama_llm": self.llm is not None,
                "vector_store": self.vector_store is not None
            }
        }

# Global instance
_enhanced_rag_system = None

def get_enhanced_rag_system() -> EnhancedRAGSystem:
    """Get global enhanced RAG system instance."""
    global _enhanced_rag_system
    if _enhanced_rag_system is None:
        _enhanced_rag_system = EnhancedRAGSystem()
    return _enhanced_rag_system

def get_enhanced_suggestion(issue_text: str, issue_type: str = "general", 
                          context: str = "") -> Dict[str, Any]:
    """Get enhanced suggestion using global RAG system."""
    rag_system = get_enhanced_rag_system()
    return rag_system.get_enhanced_suggestion(issue_text, issue_type, context)

def get_rag_status() -> Dict[str, Any]:
    """Get enhanced RAG system status."""
    rag_system = get_enhanced_rag_system()
    return rag_system.get_system_status()

if __name__ == "__main__":
    # Test the enhanced RAG system
    print("🚀 Testing Enhanced RAG System")
    print("=" * 50)
    
    rag_system = EnhancedRAGSystem()
    status = rag_system.get_system_status()
    
    print(f"System Status: {json.dumps(status, indent=2)}")
    
    if status["is_initialized"]:
        # Test with a sample issue
        test_issue = "The document was written by the author"
        print(f"\nTesting with issue: {test_issue}")
        
        result = rag_system.get_enhanced_suggestion(
            issue_text=test_issue,
            issue_type="passive_voice",
            context="Technical documentation"
        )
        
        print(f"\nEnhanced Suggestion:")
        print(f"Original: {result['original_issue']}")
        print(f"Enhanced: {result['enhanced_response']}")
        print(f"Method: {result['method']}")
        print(f"Time: {result['processing_time']:.2f}s")
    else:
        print("\nRAG system not initialized. Please check dependencies and Ollama service.")
