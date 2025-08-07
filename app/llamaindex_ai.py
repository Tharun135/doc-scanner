"""
LlamaIndex + ChromaDB + Ollama AI suggestion system for intelligent writing recommendations.
This module provides context-aware suggestions using local Ollama models (Mistral/Phi-3) + LlamaIndex RAG.

Features:
- Local Ollama AI for unlimited, free intelligent responses
- LlamaIndex RAG with ChromaDB for context-aware analysis
- Support for Mistral and Phi-3 models
- No API quotas or costs
- Natural language explanations
- Fallbacks when local AI unavailable

Setup:
1. Install Ollama: https://ollama.ai/
2. Pull models: ollama pull mistral OR ollama pull phi3
3. Start Ollama service
4. No API keys needed!
"""

import json
import re
import logging
import os
from typing import Dict, List, Optional, Any
import time

# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available - environment variables must be set manually")

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

class LlamaIndexAISuggestionEngine:
    """
    AI suggestion engine using local Ollama + LlamaIndex RAG.
    Unlimited, free AI suggestions without API quotas.
    """
    
    def __init__(self, model_name: str = "tinyllama"):
        """
        Initialize with preferred model.
        
        Args:
            model_name: "mistral", "phi3", or any other Ollama model
        """
        self.model_name = model_name
        self.llamaindex_available = LLAMAINDEX_AVAILABLE
        self.llm = None
        self.embed_model = None
        self.index = None
        self.query_engine = None
        self.chroma_client = None
        self.vector_store = None
        self.is_initialized = False
        
        if self.llamaindex_available:
            self._initialize_ollama()
        else:
            logger.warning("LlamaIndex AI system disabled - dependencies not installed")
    
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
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM and ChromaDB components."""
        try:
            # Check if Ollama service is running
            if not self._check_ollama_service():
                logger.warning("Ollama service not running. Please start Ollama: 'ollama serve'")
                return
            
            # Check if the requested model is available
            if not self._check_model_availability(self.model_name):
                logger.warning(f"Model '{self.model_name}' not found. Available alternatives:")
                logger.warning("- Pull Mistral: ollama pull mistral")
                logger.warning("- Pull Phi-3: ollama pull phi3")
                logger.warning("- Pull Llama2: ollama pull llama2")
                
                # Try fallback models
                fallback_models = ["mistral", "phi3", "llama2", "tinyllama"]
                for fallback in fallback_models:
                    if self._check_model_availability(fallback):
                        logger.info(f"Using fallback model: {fallback}")
                        self.model_name = fallback
                        break
                else:
                    logger.error("No compatible models found. Please install a model first.")
                    return
            
            # Initialize LLM
            self.llm = Ollama(
                model=self.model_name,
                request_timeout=30.0,
                temperature=0.1
            )
            
            # Initialize embedding model (using same model for embeddings)
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
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            
            # Create or get collection
            collection_name = "doc_scanner_knowledge"
            try:
                collection = self.chroma_client.get_collection(collection_name)
            except Exception:
                collection = self.chroma_client.create_collection(collection_name)
            
            # Create vector store
            self.vector_store = ChromaVectorStore(chroma_collection=collection)
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Try to load existing index or create new one
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=storage_context
                )
            except Exception:
                # Create empty index
                self.index = VectorStoreIndex([], storage_context=storage_context)
            
            # Initialize knowledge base if empty
            if len(collection.get()["ids"]) == 0:
                self._initialize_writing_knowledge()
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=3,
                response_mode="tree_summarize"
            )
            
            self.is_initialized = True
            logger.info(f"LlamaIndex AI system initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex AI system: {e}")
            self.is_initialized = False
    
    def _initialize_writing_knowledge(self):
        """Initialize the knowledge base with writing guidelines and rules."""
        writing_guidelines = [
            Document(text="""
            Writing Improvement Guidelines:
            
            1. Active Voice: Use active voice instead of passive voice for clarity.
            Example: "The team completed the project" instead of "The project was completed by the team"
            
            2. Concise Language: Remove unnecessary words and redundant phrases.
            Example: "Due to the fact that" should be "Because"
            
            3. Clear Structure: Break long sentences into shorter, clearer ones.
            Example: Split sentences longer than 25 words when possible.
            
            4. Strong Verbs: Use specific, action-oriented verbs instead of weak ones.
            Example: "Utilize" can often be "use", "facilitate" can be "help"
            
            5. Avoid Jargon: Use plain language instead of technical jargon when possible.
            Example: "Leverage" can be "use", "incentivize" can be "encourage"
            """),
            
            Document(text="""
            Common Writing Issues and Fixes:
            
            Passive Voice Patterns:
            - "is/are/was/were + past participle" → Convert to active voice
            - "The report was written by John" → "John wrote the report"
            
            Wordy Phrases:
            - "In order to" → "To"
            - "Due to the fact that" → "Because"
            - "At this point in time" → "Now"
            - "In the event that" → "If"
            
            Weak Verbs:
            - "Make use of" → "Use"
            - "Give consideration to" → "Consider"
            - "Come to a decision" → "Decide"
            """),
            
            Document(text="""
            Sentence Structure Best Practices:
            
            1. Vary sentence length for better flow
            2. Use parallel structure in lists
            3. Place important information at the beginning
            4. Use transitions between ideas
            5. Avoid run-on sentences (over 25 words)
            
            Technical Writing:
            - Use consistent terminology
            - Define acronyms on first use
            - Use numbered lists for procedures
            - Use bullet points for features or benefits
            """)
        ]
        
        # Add documents to index
        for doc in writing_guidelines:
            self.index.insert(doc)
        
        logger.info("Writing knowledge base initialized with guidelines")
    
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None,
                                     document_content: str = "") -> Dict[str, Any]:
        """
        Generate AI suggestion using local Ollama + LlamaIndex RAG.
        
        Args:
            feedback_text: The identified issue or feedback
            sentence_context: The sentence or text context
            document_type: Type of document being analyzed
            writing_goals: List of writing goals
            document_content: Full document content for context
            
        Returns:
            Dict containing suggestion, confidence, and metadata
        """
        # Safety checks for None inputs
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
        if document_content is None:
            document_content = ""
            
        try:
            # Special case: For long sentences, use rule-based splitting first
            if ("long sentence" in feedback_text.lower() or "sentence too long" in feedback_text.lower()) and sentence_context:
                logger.info("Using enhanced rule-based splitting for long sentence")
                return self.generate_smart_fallback(feedback_text, sentence_context)
            
            # Primary method: Use LlamaIndex RAG for intelligent suggestions
            if self.is_initialized and self._test_ollama_working():
                logger.info(f"Using LlamaIndex AI with model: {self.model_name}")
                
                # Create a comprehensive query for RAG
                query = self._create_rag_query(feedback_text, sentence_context, document_type)
                
                # Get RAG response with timeout protection
                response = self._safe_query_execution(query)
                
                if response:
                    # Extract suggestion from response
                    suggestion = str(response).strip()
                    
                    # Enhance with specific fixes if needed
                    enhanced_suggestion = self._enhance_suggestion(
                        suggestion, feedback_text, sentence_context
                    )
                    
                    logger.info("LlamaIndex AI suggestion generated successfully")
                    return {
                        "suggestion": enhanced_suggestion,
                        "ai_answer": suggestion,
                        "confidence": "high",
                        "method": "llamaindex_rag",
                        "model": self.model_name,
                        "sources": "local_knowledge_base",
                        "context_used": {
                            "document_type": document_type,
                            "writing_goals": writing_goals,
                            "primary_ai": "ollama_local",
                            "issue_detection": "rule_based"
                        }
                    }
                else:
                    logger.warning("Ollama query failed, using smart fallback")
            else:
                logger.warning("LlamaIndex AI not available or Ollama not working, using smart fallback")
            
            # Fallback: Smart rule-based response
            return self.generate_smart_fallback(feedback_text, sentence_context)
            
        except Exception as e:
            logger.error(f"LlamaIndex suggestion failed: {str(e)}")
            # Fall back to smart response
            return self.generate_smart_fallback(feedback_text, sentence_context)
    
    def _create_rag_query(self, feedback_text: str, sentence_context: str, document_type: str) -> str:
        """Create an effective query for RAG retrieval."""
        query_parts = []
        
        # Add the main issue
        query_parts.append(f"How to fix: {feedback_text}")
        
        # Add context if available
        if sentence_context:
            query_parts.append(f"In this sentence: '{sentence_context[:200]}'")
        
        # Add document type context
        if document_type != "general":
            query_parts.append(f"For {document_type} writing")
        
        return " ".join(query_parts)
    
    def _enhance_suggestion(self, ai_suggestion: str, feedback_text: str, sentence_context: str) -> str:
        """Enhance AI suggestion with specific, actionable advice."""
        feedback_lower = feedback_text.lower()
        
        # For passive voice issues
        if "passive voice" in feedback_lower or "active voice" in feedback_lower:
            if sentence_context:
                active_version = self._convert_to_active_voice(sentence_context)
                return f"{ai_suggestion}\n\nSpecific suggestion: {active_version}"
        
        # For long sentences
        elif "long" in feedback_lower and sentence_context:
            split_sentences = self._split_long_sentence(sentence_context)
            if len(split_sentences) > 1:
                return f"{ai_suggestion}\n\nSplit into: {' '.join(split_sentences)}"
        
        return ai_suggestion
    
    def _convert_to_active_voice(self, sentence: str) -> str:
        """Convert passive voice to active voice using pattern matching."""
        # Simple passive voice conversion patterns
        patterns = [
            (r'(\w+) was (\w+ed) by (\w+)', r'\3 \2 \1'),  # "X was done by Y" → "Y did X"
            (r'(\w+) is (\w+ed) by (\w+)', r'\3 \2s \1'),   # "X is done by Y" → "Y does X"
            (r'(\w+) are (\w+ed) by (\w+)', r'\3 \2 \1'),   # "X are done by Y" → "Y do X"
        ]
        
        result = sentence
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result if result != sentence else f"Convert to active voice: {sentence}"
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Split long sentences into shorter ones."""
        # Split on common conjunctions and punctuation
        split_points = [', and ', ', but ', ', so ', ', or ', '; ', '. ']
        
        parts = [sentence]
        for split_point in split_points:
            new_parts = []
            for part in parts:
                if split_point in part:
                    split_parts = part.split(split_point)
                    new_parts.extend([p.strip() + '.' for p in split_parts if p.strip()])
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Ensure sentences end with periods
        return [part if part.endswith('.') else part + '.' for part in parts[:3]]  # Limit to 3 sentences
    
    def generate_smart_fallback(self, feedback_text: str, sentence_context: str = "") -> Dict[str, Any]:
        """
        Generate intelligent fallback when LlamaIndex AI is unavailable.
        Provides complete sentence rewrites using rule-based logic.
        """
        # Safety checks for None inputs
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
            
        if sentence_context and sentence_context.strip():
            # Generate complete sentence rewrites based on common issues
            suggestion = self._generate_sentence_rewrite(feedback_text, sentence_context)
        else:
            suggestion = f"Writing issue detected: {feedback_text}. Please review and improve this text for clarity, grammar, and style."
        
        # Safety check: ensure suggestion is never empty
        if not suggestion or not suggestion.strip():
            suggestion = f"Review and improve this text to address: {feedback_text}"
        
        return {
            "suggestion": suggestion,
            "ai_answer": f"Review the text and address: {feedback_text}",
            "confidence": "medium",
            "method": "smart_fallback",
            "model": "rule_based",
            "note": "Using smart fallback - Local AI unavailable"
        }
    
    def _generate_sentence_rewrite(self, feedback_text: str, sentence_context: str) -> str:
        """Generate complete sentence rewrites using rule-based logic."""
        # Safety check for None inputs
        if feedback_text is None:
            feedback_text = "general improvement needed"
        if sentence_context is None:
            sentence_context = ""
            
        feedback_lower = str(feedback_text).lower()
        
        # Passive voice fixes
        if "passive voice" in feedback_lower or "active voice" in feedback_lower:
            return self._convert_to_active_voice(sentence_context)
        
        # Long sentence fixes
        elif "long" in feedback_lower or "sentence too long" in feedback_lower:
            split_sentences = self._split_long_sentence(sentence_context)
            return " ".join(split_sentences)
        
        # First person fixes
        elif "first person" in feedback_lower:
            return sentence_context.replace("We recommend", "Consider").replace("we recommend", "consider")
        
        # Default improvement
        else:
            return self._apply_general_improvements(sentence_context)
    
    def _apply_general_improvements(self, text: str) -> str:
        """Apply general improvements to text"""
        if not text:
            return "Please provide specific text to improve."
        
        # Remove redundant words
        improved = text.replace("really really", "very")
        improved = improved.replace("very very", "extremely")
        
        # Fix common issues
        improved = improved.replace("due to the fact that", "because")
        improved = improved.replace("in order to", "to")
        improved = improved.replace("at this point in time", "now")
        
        return improved if improved != text else f"Consider revising: {text}"
    
    def _test_ollama_working(self) -> bool:
        """Test if Ollama can actually process requests (not just running)"""
        try:
            if not self._check_ollama_service():
                return False
            
            # Try a simple request to test if model actually works
            test_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "Test",
                    "stream": False
                },
                timeout=10
            )
            
            return test_response.status_code == 200 and "response" in test_response.json()
        except Exception as e:
            logger.warning(f"Ollama test failed: {e}")
            return False
    
    def _safe_query_execution(self, query: str):
        """Execute RAG query with timeout and error handling"""
        try:
            # Set a reasonable timeout for local processing
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Query execution timed out")
            
            # Use timeout for query execution
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(20)  # 20 second timeout
            
            try:
                response = self.query_engine.query(query)
                signal.alarm(0)  # Cancel timeout
                return response
            except TimeoutError:
                logger.warning("RAG query timed out")
                return None
            finally:
                signal.alarm(0)  # Ensure timeout is cancelled
                
        except Exception as e:
            logger.warning(f"Safe query execution failed: {e}")
            return None
        else:
            return f"Improve this text: {sentence_context}"
    
    def add_document_to_knowledge(self, content: str, metadata: Dict[str, Any] = None):
        """Add a document to the knowledge base for future reference."""
        if not self.is_initialized:
            return False
        
        try:
            doc = Document(text=content, metadata=metadata or {})
            self.index.insert(doc)
            logger.info("Document added to knowledge base")
            return True
        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the AI system."""
        return {
            "initialized": self.is_initialized,
            "model": self.model_name,
            "ollama_running": self._check_ollama_service(),
            "model_available": self._check_model_availability(self.model_name),
            "system_type": "LlamaIndex + ChromaDB + Ollama",
            "cost": "Free (Local)",
            "quota": "Unlimited"
        }


# Global instance for easy import
llamaindex_ai_engine = LlamaIndexAISuggestionEngine()

def get_ai_suggestion(feedback_text: str, sentence_context: str = "", 
                     document_type: str = "general", 
                     writing_goals: List[str] = None,
                     document_content: str = "") -> Dict[str, Any]:
    """
    Convenience function to get AI suggestions.
    
    This function provides the same interface as the previous Gemini system
    but uses local LlamaIndex + Ollama instead.
    """
    return llamaindex_ai_engine.generate_contextual_suggestion(
        feedback_text=feedback_text,
        sentence_context=sentence_context,
        document_type=document_type,
        writing_goals=writing_goals,
        document_content=document_content
    )
