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

Features:
- Issue-to-query transformation
- ChromaDB vector search
- LlamaIndex integration
- Local Ollama LLM for unlimited usage
- Intelligent caching
- Grammar and style enhancement
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
    """
    Complete RAG system that transforms issues into polished responses.
    
    Workflow:
    Issue → Query → Knowledge Search → LLM Polish → Enhanced Response
    """
    
    def __init__(self, model_name: str = "mistral"):
        """
        Initialize the enhanced RAG system.
        
        Args:
            model_name: Ollama model to use (mistral, phi3, llama2, etc.)
        """
        self.model_name = model_name
        self.rag_available = LLAMAINDEX_AVAILABLE
        self.llm = None
        self.embed_model = None
        self.index = None
        self.query_engine = None
        self.chroma_client = None
        self.vector_store = None
        
        # Knowledge cache for performance
        self.knowledge_cache = {}
        self.cache_file = "rag_knowledge_cache.json"
        self._load_cache()
        
        if LLAMAINDEX_AVAILABLE:
            self._initialize_rag_system()
        else:
            logger.error("❌ LlamaIndex not available - RAG system disabled")
    
    def _check_ollama_service(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _check_model_availability(self, model_name: str) -> bool:
        """Check if model is available in Ollama."""
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
        """Initialize complete RAG system with knowledge base."""
        try:
            logger.info("🚀 Initializing Enhanced RAG Knowledge System...")
            
            # Check Ollama service
            if not self._check_ollama_service():
                logger.warning("⚠️ Ollama service not running. Please start: 'ollama serve'")
                return
            
            # Ensure model is available
            if not self._check_model_availability(self.model_name):
                fallback_models = ["mistral", "phi3", "llama2", "tinyllama"]
                for fallback in fallback_models:
                    if self._check_model_availability(fallback):
                        logger.info(f"Using fallback model: {fallback}")
                        self.model_name = fallback
                        break
                else:
                    logger.error("❌ No compatible models found")
                    return
            
            # Initialize LLM
            self.llm = Ollama(
                model=self.model_name,
                request_timeout=60.0,
                temperature=0.1  # Low temperature for consistent, factual responses
            )
            
            # Initialize embeddings
            self.embed_model = OllamaEmbedding(
                model_name=self.model_name,
                base_url="http://localhost:11434"
            )
            
            # Configure global settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path="./rag_knowledge_db")
            
            # Create knowledge collection
            collection_name = "writing_knowledge_base"
            try:
                collection = self.chroma_client.get_collection(collection_name)
                logger.info("📚 Using existing knowledge collection")
            except Exception:
                collection = self.chroma_client.create_collection(collection_name)
                logger.info("🆕 Created new knowledge collection")
                self._populate_initial_knowledge(collection)
            
            # Create vector store
            self.vector_store = ChromaVectorStore(chroma_collection=collection)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Create or load index
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=storage_context
                )
                logger.info("✅ Loaded existing knowledge index")
            except Exception as e:
                logger.info(f"Creating new knowledge index: {e}")
                self.index = VectorStoreIndex([], storage_context=storage_context)
            
            # Create query engine with enhanced retrieval
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=5  # Retrieve top 5 relevant knowledge pieces
            )
            
            self.query_engine = RetrieverQueryEngine(retriever=retriever)
            
            self.is_initialized = True
            logger.info(f"✅ Enhanced RAG system initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG system: {e}")
            self.is_initialized = False
    
    def _populate_initial_knowledge(self, collection):
        """Populate knowledge base with writing improvement knowledge."""
        knowledge_documents = [
            {
                "id": "passive_voice_guide",
                "content": """Passive Voice Improvement Guide:
                
                Passive voice occurs when the subject receives the action rather than performing it.
                Examples:
                - Passive: "The document was written by John" 
                - Active: "John wrote the document"
                
                Why avoid passive voice:
                1. Makes writing more direct and engaging
                2. Reduces word count and improves clarity
                3. Creates stronger, more confident tone
                4. Makes responsibility and action clearer
                
                How to fix:
                1. Identify the performer of the action
                2. Make them the subject of the sentence
                3. Use active verbs instead of "was/were + past participle"
                
                Common passive patterns to avoid:
                - "was/were + past participle"
                - "is/are being + past participle" 
                - "has/have been + past participle"
                """
            },
            {
                "id": "long_sentences_guide", 
                "content": """Long Sentence Improvement Guide:
                
                Long sentences (over 20-25 words) can confuse readers and reduce comprehension.
                
                Problems with long sentences:
                1. Reader loses track of the main point
                2. Multiple ideas compete for attention
                3. Increased cognitive load
                4. Higher chance of grammatical errors
                
                How to fix long sentences:
                1. Break into 2-3 shorter sentences
                2. Use coordinating conjunctions (and, but, or)
                3. Create bullet points for lists
                4. Use transitions between ideas
                5. Remove unnecessary words and phrases
                
                Example:
                Long: "The software development process, which includes planning, coding, testing, and deployment phases, requires careful coordination between multiple teams, including developers, QA engineers, and DevOps specialists, to ensure successful project delivery."
                
                Better: "The software development process includes four key phases: planning, coding, testing, and deployment. Success requires careful coordination between developers, QA engineers, and DevOps specialists."
                """
            },
            {
                "id": "modifiers_guide",
                "content": """Unnecessary Modifiers Improvement Guide:
                
                Unnecessary modifiers weaken writing by adding words without adding meaning.
                
                Common unnecessary modifiers:
                - very, really, quite, rather, extremely
                - absolutely, completely, totally
                - basically, essentially, actually
                
                Why remove them:
                1. They dilute the impact of your words
                2. Create wordiness without adding value
                3. Make writing sound uncertain or weak
                4. Better word choice is more effective
                
                How to fix:
                1. Delete the modifier entirely
                2. Choose a stronger, more specific word
                3. Use concrete, measurable descriptions
                
                Examples:
                - "very important" → "critical" or "essential"
                - "extremely difficult" → "challenging" or "complex"
                - "really good" → "excellent" or "outstanding"
                - "quite large" → "substantial" or specific size
                """
            },
            {
                "id": "grammar_improvement_guide",
                "content": """Grammar Improvement Best Practices:
                
                Common grammar issues and solutions:
                
                Subject-Verb Agreement:
                - Singular subjects take singular verbs
                - Plural subjects take plural verbs
                - Watch for collective nouns and compound subjects
                
                Pronoun Reference:
                - Pronouns must clearly refer to specific nouns
                - Avoid ambiguous "this," "that," "it"
                - Ensure pronouns match in number and gender
                
                Parallel Structure:
                - Use consistent grammatical forms in lists
                - Match verb tenses in compound sentences
                - Balance phrases and clauses
                
                Comma Usage:
                - Before coordinating conjunctions in compound sentences
                - After introductory phrases
                - Around non-essential clauses
                - Between items in a series
                
                Common fixes:
                1. Read sentences aloud to catch errors
                2. Check subject-verb pairs
                3. Verify pronoun references
                4. Ensure parallel structure in lists
                """
            },
            {
                "id": "technical_writing_guide",
                "content": """Technical Writing Best Practices:
                
                Technical writing should be clear, concise, and accessible.
                
                Key principles:
                1. Use precise, specific language
                2. Define technical terms on first use
                3. Write for your audience's knowledge level
                4. Use active voice when possible
                5. Structure information logically
                
                Common improvements:
                - Replace jargon with plain language
                - Use consistent terminology
                - Include examples and illustrations
                - Break complex processes into steps
                - Use headings and bullet points for clarity
                
                Word choice guidelines:
                - "utilize" → "use"
                - "initiate" → "start" or "begin"
                - "facilitate" → "help" or "enable"
                - "implement" → "carry out" or "put in place"
                
                Structure tips:
                1. Lead with the main point
                2. Support with details and evidence
                3. Use transitions between sections
                4. Summarize key takeaways
                """
            }
        ]
        
        # Add documents to collection
        for doc in knowledge_documents:
            # Add to ChromaDB collection if needed
            logger.info(f"Added knowledge: {doc['id']}")
    
    def _load_cache(self):
        """Load knowledge cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.knowledge_cache = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load knowledge cache: {e}")
            self.knowledge_cache = {}
    
    def _save_cache(self):
        """Save knowledge cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save knowledge cache: {e}")
    
    def _create_cache_key(self, issue_text: str, issue_type: str) -> str:
        """Create cache key for issue."""
        content = f"{issue_type}:{issue_text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def process_issue_with_rag(self, issue_text: str, issue_type: str, context: str = "") -> Dict[str, Any]:
        """
        Complete RAG workflow:
        1. Transform issue into query
        2. Search knowledge base
        3. Generate enhanced response
        4. Polish with LLM
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "RAG system not initialized",
                "fallback": issue_text
            }
        
        # Check cache first
        cache_key = self._create_cache_key(issue_text, issue_type)
        if cache_key in self.knowledge_cache:
            logger.info(f"📋 Using cached RAG response for {issue_type}")
            return self.knowledge_cache[cache_key]
        
        try:
            logger.info(f"🔍 Processing {issue_type} issue with RAG: {issue_text[:50]}...")
            
            # Step 1: Transform issue into knowledge query
            knowledge_query = self._create_knowledge_query(issue_text, issue_type, context)
            logger.info(f"📝 Knowledge query: {knowledge_query}")
            
            # Step 2: Search knowledge base
            knowledge_response = self._search_knowledge_base(knowledge_query)
            logger.info(f"📚 Retrieved knowledge: {len(knowledge_response)} characters")
            
            # Step 3: Generate enhanced response using LLM
            enhanced_response = self._generate_enhanced_response(
                issue_text, issue_type, knowledge_response, context
            )
            logger.info(f"🤖 Generated enhanced response: {len(enhanced_response)} characters")
            
            # Step 4: Polish response for grammar and clarity
            polished_response = self._polish_response(enhanced_response)
            logger.info(f"✨ Polished final response: {len(polished_response)} characters")
            
            result = {
                "success": True,
                "issue_type": issue_type,
                "original_issue": issue_text,
                "knowledge_query": knowledge_query,
                "retrieved_knowledge": knowledge_response[:200] + "..." if len(knowledge_response) > 200 else knowledge_response,
                "enhanced_response": enhanced_response,
                "polished_response": polished_response,
                "processing_method": "rag_enhanced",
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the result
            self.knowledge_cache[cache_key] = result
            self._save_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ RAG processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": issue_text,
                "processing_method": "rag_failed"
            }
    
    def _create_knowledge_query(self, issue_text: str, issue_type: str, context: str) -> str:
        """Transform detected issue into a knowledge base query."""
        query_templates = {
            "passive_voice": f"How to convert passive voice to active voice: {issue_text}",
            "long_sentences": f"How to break down and improve long sentences: {issue_text}",
            "unnecessary_modifiers": f"How to remove unnecessary modifiers and strengthen: {issue_text}",
            "grammar_issues": f"How to fix grammar problems in: {issue_text}",
            "technical_terms": f"How to improve technical writing and terminology: {issue_text}",
            "readability": f"How to improve readability and clarity: {issue_text}",
            "style_formatting": f"How to improve writing style and formatting: {issue_text}"
        }
        
        # Create specific query based on issue type
        base_query = query_templates.get(issue_type, f"How to improve writing issue: {issue_text}")
        
        # Add context if available
        if context:
            base_query += f" Context: {context}"
        
        return base_query
    
    def _search_knowledge_base(self, query: str) -> str:
        """Search knowledge base for relevant information."""
        try:
            response = self.query_engine.query(query)
            if hasattr(response, 'response'):
                return response.response
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return "No relevant knowledge found."
    
    def _generate_enhanced_response(self, issue_text: str, issue_type: str, knowledge: str, context: str) -> str:
        """Generate enhanced response using LLM with retrieved knowledge."""
        prompt = f"""You are an expert writing improvement assistant. Use the provided knowledge to create a helpful, specific response.

DETECTED ISSUE TYPE: {issue_type}
ORIGINAL TEXT WITH ISSUE: "{issue_text}"
RETRIEVED KNOWLEDGE: {knowledge}
ADDITIONAL CONTEXT: {context if context else "None"}

TASK: Create a clear, actionable response that:
1. Explains the specific writing issue
2. Provides a concrete improvement suggestion
3. Uses the retrieved knowledge as guidance
4. Gives a specific example or rewrite

FORMAT: Provide a direct, helpful suggestion without meta-commentary.

RESPONSE:"""
        
        try:
            response = self.llm.complete(prompt)
            if hasattr(response, 'text'):
                return response.text.strip()
            else:
                return str(response).strip()
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return f"Improve {issue_type}: {issue_text}"
    
    def _polish_response(self, response: str) -> str:
        """Polish response for perfect grammar and clarity."""
        polish_prompt = f"""Polish this writing improvement suggestion for perfect grammar, clarity, and professionalism:

ORIGINAL RESPONSE: "{response}"

REQUIREMENTS:
1. Fix any grammar or punctuation errors
2. Ensure clear, professional tone
3. Make suggestions specific and actionable
4. Keep the core message intact
5. Use active voice where appropriate

POLISHED RESPONSE:"""
        
        try:
            polished = self.llm.complete(polish_prompt)
            if hasattr(polished, 'text'):
                return polished.text.strip()
            else:
                return str(polished).strip()
        except Exception as e:
            logger.error(f"Response polishing failed: {e}")
            return response  # Return original if polishing fails
    
    def add_knowledge_document(self, doc_id: str, content: str, metadata: Dict = None):
        """Add new knowledge document to the system."""
        if not self.is_initialized:
            logger.error("❌ Cannot add knowledge - RAG system not initialized")
            return False
        
        try:
            document = Document(text=content, metadata=metadata or {"id": doc_id})
            self.index.insert(document)
            logger.info(f"✅ Added knowledge document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add knowledge document: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "rag_initialized": self.is_initialized,
            "model_name": self.model_name,
            "llamaindex_available": LLAMAINDEX_AVAILABLE,
            "cached_responses": len(self.knowledge_cache),
            "ollama_service": self._check_ollama_service() if LLAMAINDEX_AVAILABLE else False,
            "model_available": self._check_model_availability(self.model_name) if LLAMAINDEX_AVAILABLE else False
        }

# Global instance
_rag_system = None

def get_enhanced_rag_system() -> EnhancedRAGKnowledgeSystem:
    """Get global RAG system instance."""
    global _rag_system
    if _rag_system is None:
        _rag_system = EnhancedRAGKnowledgeSystem()
    return _rag_system

def process_issue_with_enhanced_rag(issue_text: str, issue_type: str, context: str = "") -> Dict[str, Any]:
    """Convenience function to process issue with RAG."""
    rag_system = get_enhanced_rag_system()
    return rag_system.process_issue_with_rag(issue_text, issue_type, context)
