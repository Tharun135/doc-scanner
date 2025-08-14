"""
Enhanced RAG System for Writing Rules
Searches vector database for specific rule solutions, then uses LLM to polish the response.
Falls back to simplified keyword-based matching if dependencies are not available.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from .knowledge_base import WRITING_RULES_KNOWLEDGE_BASE

# Try to import LlamaIndex components
LLAMAINDEX_AVAILABLE = False
try:
    from llama_index.core import VectorStoreIndex, Document, Settings, ServiceContext
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logging.warning(f"LlamaIndex not available: {e}")

logger = logging.getLogger(__name__)

class WritingRulesRAG:
    """
    Advanced RAG system for writing rules that:
    1. Stores writing rules in vector database
    2. Retrieves most relevant rules for detected issues
    3. Uses LLM to polish and contextualize the solution
    """
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.rules_index = None
        self.query_engine = None
        self.initialized = False
        
        if LLAMAINDEX_AVAILABLE:
            self._initialize_rag_system()
        else:
            logger.warning("LlamaIndex not available - using fallback responses")
    
    def _initialize_rag_system(self):
        """Initialize the RAG system with writing rules knowledge base."""
        try:
            # Configure LlamaIndex settings
            Settings.llm = Ollama(model=self.model_name, request_timeout=60.0)
            Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
            Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=50)
            
            # Create documents from knowledge base
            documents = self._create_rule_documents()
            
            # Build vector index
            self.rules_index = VectorStoreIndex.from_documents(documents)
            
            # Create specialized query engine for rule retrieval
            retriever = VectorIndexRetriever(
                index=self.rules_index,
                similarity_top_k=3  # Get top 3 most relevant rules
            )
            
            self.query_engine = RetrieverQueryEngine(retriever=retriever)
            
            self.initialized = True
            logger.info(f"Writing Rules RAG system initialized with {len(documents)} rule documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.initialized = False
    
    def _create_rule_documents(self) -> List[Document]:
        """Convert writing rules knowledge base into LlamaIndex documents."""
        documents = []
        
        for category, rules in WRITING_RULES_KNOWLEDGE_BASE.items():
            for rule in rules:
                # Create a comprehensive document for each rule
                rule_text = self._format_rule_for_indexing(rule)
                
                metadata = {
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "rule_title": rule["rule_title"],
                    "issue_pattern": rule["issue_pattern"],
                    "keywords": rule["keywords"]
                }
                
                doc = Document(text=rule_text, metadata=metadata)
                documents.append(doc)
        
        return documents
    
    def _format_rule_for_indexing(self, rule: Dict[str, Any]) -> str:
        """Format a rule into searchable text for vector indexing."""
        formatted_text = f"""
RULE: {rule['rule_title']}

ISSUE PATTERN: {rule['issue_pattern']}
CATEGORY: {rule['category']}
SEVERITY: {rule['severity']}

PROBLEM: {rule['issue_description']}

SOLUTION: {rule['solution']}

EXAMPLES:
"""
        
        for i, example in enumerate(rule.get('examples', []), 1):
            formatted_text += f"""
Example {i}:
❌ WRONG: {example['wrong']}
✅ CORRECT: {example['right']}
💡 EXPLANATION: {example['explanation']}
"""
        
        # Add keywords for better searchability
        formatted_text += f"\nKEYWORDS: {', '.join(rule['keywords'])}"
        
        return formatted_text
    
    def get_rule_based_suggestion(self, 
                                issue_text: str, 
                                sentence_context: str, 
                                category: str = "general") -> Dict[str, Any]:
        """
        Get a rule-based suggestion using RAG:
        1. Search vector database for relevant rules
        2. Use LLM to polish and contextualize the solution
        """
        
        if not self.initialized or not LLAMAINDEX_AVAILABLE:
            return self._fallback_suggestion(issue_text, sentence_context, category)
        
        try:
            # Create a comprehensive query combining issue and context
            query = f"""
            Writing issue: {issue_text}
            Sentence context: {sentence_context}
            Category: {category}
            
            Find the most relevant writing rule and solution for this issue.
            """
            
            # Retrieve relevant rules from vector database
            response = self.query_engine.query(query)
            
            # Extract retrieved rule information
            retrieved_rules = self._extract_retrieved_rules(response)
            
            # Use LLM to create polished, contextual suggestion
            polished_suggestion = self._polish_suggestion_with_llm(
                issue_text, sentence_context, retrieved_rules, category
            )
            
            return {
                "suggestion": polished_suggestion,
                "confidence": 0.9,
                "source": "RAG + LLM",
                "retrieved_rules": len(retrieved_rules),
                "rule_based": True
            }
            
        except Exception as e:
            logger.error(f"Error in RAG suggestion: {e}")
            return self._fallback_suggestion(issue_text, sentence_context, category)
    
    def _extract_retrieved_rules(self, response) -> List[Dict[str, Any]]:
        """Extract structured rule information from RAG response."""
        # This would extract the most relevant rules from the response
        # For now, return a simplified structure
        return [{"rule_content": str(response)}]
    
    def _polish_suggestion_with_llm(self, 
                                  issue_text: str, 
                                  sentence_context: str, 
                                  retrieved_rules: List[Dict], 
                                  category: str) -> str:
        """Use LLM to polish the retrieved rule into a contextual suggestion."""
        
        if not self.initialized:
            return f"Issue detected: {issue_text}. Please check writing guidelines for {category}."
        
        try:
            # Create a focused prompt for the LLM
            polish_prompt = f"""
Based on the writing rule below, provide a specific, actionable suggestion for this issue:

ISSUE: {issue_text}
SENTENCE: "{sentence_context}"
CATEGORY: {category}

RELEVANT WRITING RULE:
{retrieved_rules[0]['rule_content'] if retrieved_rules else 'No specific rule found'}

Provide a concise, helpful suggestion that:
1. Explains what's wrong
2. Shows how to fix it
3. Gives a specific rewritten example if applicable

Keep the response under 150 words and make it actionable.
"""
            
            # Use the LLM to polish the suggestion
            llm_response = Settings.llm.complete(polish_prompt)
            return str(llm_response)
            
        except Exception as e:
            logger.error(f"Error polishing suggestion with LLM: {e}")
            return f"Writing issue detected: {issue_text}. Consider revising for better {category}."
    
    def _fallback_suggestion(self, issue_text: str, sentence_context: str, category: str) -> Dict[str, Any]:
        """Fallback suggestion when RAG system is not available."""
        return {
            "suggestion": f"Writing issue detected: {issue_text}. Please review the sentence for {category} improvements.",
            "confidence": 0.5,
            "source": "fallback",
            "retrieved_rules": 0,
            "rule_based": False
        }
    
    def add_new_rule(self, rule: Dict[str, Any]) -> bool:
        """Add a new rule to the knowledge base and re-index."""
        try:
            # Add to appropriate category in knowledge base
            category_key = f"{rule['category']}_rules"
            if category_key not in WRITING_RULES_KNOWLEDGE_BASE:
                WRITING_RULES_KNOWLEDGE_BASE[category_key] = []
            
            WRITING_RULES_KNOWLEDGE_BASE[category_key].append(rule)
            
            # Re-initialize the RAG system with updated rules
            if self.initialized:
                self._initialize_rag_system()
            
            logger.info(f"Added new rule: {rule['rule_title']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding new rule: {e}")
            return False
    
    def search_similar_rules(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar rules in the knowledge base."""
        if not self.initialized:
            return []
        
        try:
            response = self.query_engine.query(f"Find rules similar to: {query}")
            # Process and return structured results
            return [{"rule": str(response), "similarity": 0.8}]
            
        except Exception as e:
            logger.error(f"Error searching similar rules: {e}")
            return []

# Global RAG instance - try full RAG first, fallback to simplified
if LLAMAINDEX_AVAILABLE:
    try:
        writing_rag = WritingRulesRAG()
        if not writing_rag.initialized:
            raise ImportError("Full RAG system not available")
    except Exception as e:
        logger.warning(f"Full RAG system not available ({e}), using simplified version")
        from .simplified_rag import simplified_rag as writing_rag
else:
    logger.info("Using simplified RAG system (LlamaIndex not available)")
    from .simplified_rag import simplified_rag as writing_rag

def get_rag_suggestion(issue_text: str, sentence_context: str, category: str = "general") -> Dict[str, Any]:
    """
    Main function to get RAG-based suggestions.
    Uses full RAG system if available, otherwise falls back to simplified version.
    """
    if hasattr(writing_rag, 'get_rule_based_suggestion'):
        return writing_rag.get_rule_based_suggestion(issue_text, sentence_context, category)
    else:
        # Fallback for older interface
        return writing_rag.get_enhanced_ai_suggestion(issue_text, sentence_context, category)

def is_rag_available() -> bool:
    """Check if RAG system is properly initialized."""
    return getattr(writing_rag, 'initialized', False)

def add_writing_rule(rule: Dict[str, Any]) -> bool:
    """Add a new writing rule to the RAG system."""
    if hasattr(writing_rag, 'add_new_rule'):
        return writing_rag.add_new_rule(rule)
    else:
        logger.warning("Rule addition not supported in current RAG implementation")
        return False
