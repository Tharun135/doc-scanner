"""
Production-ready Ollama RAG System for DocScanner
Uses TinyLLaMA (or available models) for local, private AI suggestions.
"""

import os
import logging
import subprocess
from typing import Dict, List, Optional, Any
import json

try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore
    import chromadb
    OLLAMA_AVAILABLE = True
    logging.info("Ollama RAG dependencies loaded successfully")
except ImportError as e:
    OLLAMA_AVAILABLE = False
    logging.warning(f"Ollama RAG dependencies not available: {e}")

logger = logging.getLogger(__name__)

class DocScannerOllamaRAG:
    """
    Production Ollama RAG system for DocScanner.
    Auto-detects available models and provides writing suggestions.
    """
    
    def __init__(self):
        self.model = None
        self.llm = None
        self.embed_model = None
        self.index = None
        self.query_engine = None
        self.is_initialized = False
        
        if OLLAMA_AVAILABLE:
            self._auto_initialize()
    
    def _get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])  # Full name with tag
                return models
        except Exception as e:
            logger.error(f"Could not get Ollama models: {e}")
        return []
    
    def _auto_initialize(self):
        """Auto-initialize with best available model"""
        try:
            models = self._get_available_models()
            if not models:
                logger.error("No Ollama models found")
                return
            
            # Prefer models in this order for writing tasks
            preferred = ['mistral', 'phi3', 'llama', 'tinyllama']
            
            # Find best available model
            best_model = None
            for pref in preferred:
                for model in models:
                    if pref in model.lower():
                        best_model = model
                        break
                if best_model:
                    break
            
            if not best_model:
                best_model = models[0]  # Use first available
            
            # Try to initialize with the selected model
            success = self._initialize_with_model(best_model)
            if success:
                logger.info(f"Ollama RAG initialized with {best_model}")
            else:
                # Try other models if first fails
                for model in models:
                    if model != best_model:
                        success = self._initialize_with_model(model)
                        if success:
                            logger.info(f"Ollama RAG initialized with fallback {model}")
                            break
                
        except Exception as e:
            logger.error(f"Auto-initialization failed: {e}")
    
    def _initialize_with_model(self, model_name: str) -> bool:
        """Initialize RAG system with specific model"""
        try:
            self.model = model_name
            
            # Initialize LLM
            self.llm = Ollama(
                model=model_name,
                request_timeout=30.0,
                temperature=0.1
            )
            
            # Use same model for embeddings (simpler and often works)
            self.embed_model = OllamaEmbedding(model_name=model_name)
            
            # Set global settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            
            # Test basic functionality
            test_response = self.llm.complete("Test")
            if not test_response:
                return False
            
            # Create knowledge base
            self._create_writing_knowledge_base()
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize with {model_name}: {e}")
            return False
    
    def _create_writing_knowledge_base(self):
        """Create vector knowledge base of writing rules"""
        try:
            # Default writing rules knowledge
            rules = [
                {
                    "text": "Convert passive voice to active voice. Change 'was written by John' to 'John wrote'. Put the actor first, then the action.",
                    "category": "passive_voice"
                },
                {
                    "text": "Break long sentences into shorter ones. Aim for 15-20 words per sentence. Split at conjunctions and use periods.",
                    "category": "sentence_length"  
                },
                {
                    "text": "Replace weak verbs like 'is', 'are', 'have' with strong action verbs. Use 'manages' instead of 'is responsible for'.",
                    "category": "weak_verbs"
                },
                {
                    "text": "Use definitive language instead of modal verbs. Replace 'might' with 'will', 'could' with 'can', 'should' with 'must'.",
                    "category": "modal_verbs"
                },
                {
                    "text": "Write in present tense for instructions. Use 'Click the button' instead of 'The button should be clicked'.",
                    "category": "technical_writing"
                }
            ]
            
            # Load custom rules if available
            custom_rules = self._load_custom_rules()
            if custom_rules:
                rules.extend(custom_rules)
                logger.info(f"Added {len(custom_rules)} custom writing rules")
            
            # Convert to documents
            documents = [
                Document(
                    text=rule["text"],
                    metadata={"category": rule["category"]}
                ) for rule in rules
            ]
            
            # Create vector index
            self.index = VectorStoreIndex.from_documents(documents)
            self.query_engine = self.index.as_query_engine(similarity_top_k=2)
            
            logger.info(f"Knowledge base created with {len(rules)} rules")
            
        except Exception as e:
            logger.warning(f"Could not create knowledge base: {e}")
            # Create minimal index for basic functionality
            doc = Document(text="Improve writing clarity and directness.")
            self.index = VectorStoreIndex.from_documents([doc])
            self.query_engine = self.index.as_query_engine()
    
    def _load_custom_rules(self):
        """Load custom writing rules from JSON file"""
        custom_file = "custom_writing_rules.json"
        if os.path.exists(custom_file):
            try:
                with open(custom_file, 'r') as f:
                    custom_rules_data = json.load(f)
                
                # Convert to expected format
                custom_rules = []
                for rule_data in custom_rules_data:
                    rule_text = rule_data.get('text', '')
                    if rule_text:
                        # Add examples to the rule text if available
                        examples = rule_data.get('examples', [])
                        if examples and isinstance(examples, list):
                            example_text = " Examples: " + ", ".join([ex.strip() for ex in examples if ex.strip()])
                            rule_text += example_text
                        
                        custom_rules.append({
                            "text": rule_text,
                            "category": rule_data.get('category', 'custom')
                        })
                
                logger.info(f"Loaded {len(custom_rules)} custom writing rules")
                return custom_rules
                
            except Exception as e:
                logger.warning(f"Could not load custom rules: {e}")
        return []
    
    def get_rag_suggestion(self, feedback_text: str, sentence_context: str = "",
                          document_type: str = "general", 
                          document_content: str = "") -> Optional[Dict[str, Any]]:
        """
        Generate writing suggestion using local Ollama RAG.
        
        Args:
            feedback_text: Description of the writing issue
            sentence_context: The problematic sentence
            document_type: Type of document
            document_content: Full document content
            
        Returns:
            Dict with suggestion, confidence, method, and metadata
        """
        
        if not self.is_initialized:
            return None
        
        try:
            # Create focused query for writing improvement
            query = f"""Rewrite this sentence to fix: {feedback_text}

Original: {sentence_context}

Rewrite:"""
            
            # Get RAG response
            response = self.query_engine.query(query)
            suggestion_text = str(response).strip()
            
            # Clean up the response
            suggestion_text = self._clean_suggestion(suggestion_text, sentence_context)
            
            return {
                "suggestion": suggestion_text,
                "confidence": "medium",
                "method": "ollama_local_rag", 
                "model": self.model,
                "sources": [],
                "context_used": {
                    "document_type": document_type,
                    "local_ai": True,
                    "private": True,
                    "cost": "free"
                }
            }
            
        except Exception as e:
            logger.error(f"RAG suggestion failed: {e}")
            return None
    
    def _clean_suggestion(self, raw_suggestion: str, original_sentence: str) -> str:
        """Clean and format the RAG suggestion"""
        
        suggestion = raw_suggestion.strip()
        
        # Remove common verbose prefixes from TinyLLaMA
        verbose_prefixes = [
            "In response to the given context information and not prior knowledge",
            "Here's a rewritten version:",
            "Here is a revised version:",
            "Improved sentence:",
            "Better version:",
            "Rewrite:",
            "Fixed version:",
            "Here's the rewrite:",
            "The rewritten sentence:",
            "A better version would be:",
        ]
        
        for prefix in verbose_prefixes:
            if suggestion.lower().startswith(prefix.lower()):
                suggestion = suggestion[len(prefix):].strip()
                break
        
        # Remove trailing explanations after colons or periods
        if ':' in suggestion:
            # If there's a colon, take everything after it as the main suggestion
            parts = suggestion.split(':', 1)
            if len(parts) > 1:
                suggestion = parts[1].strip()
        
        # Look for actual sentence improvements in quotes
        import re
        quoted_match = re.search(r'"([^"]*)"', suggestion)
        if quoted_match:
            quoted_text = quoted_match.group(1).strip()
            # Use quoted text if it's different from original and reasonable length
            if (quoted_text.lower() != original_sentence.lower() and 
                10 < len(quoted_text) < 300 and
                not quoted_text.lower().startswith('date and time picker')):  # Avoid exact matches
                suggestion = quoted_text
        
        # Try to extract the main sentence if it starts with common patterns
        sentence_patterns = [
            r'^Instructions?:\s*(.+)',
            r'^Rewrite:\s*(.+)',
            r'^Better:\s*(.+)',
            r'^Fixed:\s*(.+)',
        ]
        
        for pattern in sentence_patterns:
            match = re.search(pattern, suggestion, re.IGNORECASE)
            if match:
                potential_sentence = match.group(1).strip()
                if len(potential_sentence) > 10:
                    suggestion = potential_sentence
                    break
        
        # Remove explanatory text after the main suggestion
        # Look for common patterns that indicate explanations
        explanation_patterns = [
            r'\.\s+(This|The|It|That)',
            r'\.\s+(Instead|Rather|Better)',
            r'\n\n',
            r'Question:',
            r'Explanation:',
            r'Note:',
        ]
        
        for pattern in explanation_patterns:
            match = re.search(pattern, suggestion, re.IGNORECASE)
            if match:
                suggestion = suggestion[:match.start()].strip()
                if suggestion.endswith('.'):
                    break
        
        # Clean up remaining artifacts
        suggestion = suggestion.strip(' ."')
        
        # If suggestion is too similar to original, provide a generic improvement
        if (suggestion.lower().strip() == original_sentence.lower().strip() or
            len(suggestion.strip()) < 10):
            suggestion = "Consider rewriting this sentence for better clarity and directness."
        
        # Ensure it's not too long
        if len(suggestion) > 200:
            suggestion = suggestion[:200].strip()
            # Try to end at a complete word
            if ' ' in suggestion:
                suggestion = ' '.join(suggestion.split(' ')[:-1])
        
        return suggestion
    
    def test_system(self) -> Dict[str, Any]:
        """Test the RAG system and return status"""
        if not OLLAMA_AVAILABLE:
            return {
                "status": "failed",
                "reason": "Dependencies not installed", 
                "available": False
            }
        
        if not self.is_initialized:
            return {
                "status": "failed",
                "reason": "Could not initialize with available models",
                "available": False
            }
        
        try:
            # Test with sample writing issue
            test_result = self.get_rag_suggestion(
                feedback_text="Passive voice detected",
                sentence_context="The document was written by John.",
                document_type="technical"
            )
            
            if test_result:
                return {
                    "status": "success",
                    "model": self.model,
                    "available": True,
                    "suggestion_preview": test_result["suggestion"][:100] + "...",
                    "benefits": ["🏠 Private", "⚡ Fast", "💰 Free", "🔒 Local"]
                }
            else:
                return {
                    "status": "failed",
                    "reason": "No suggestion generated",
                    "available": False
                }
                
        except Exception as e:
            return {
                "status": "failed", 
                "reason": str(e),
                "available": False
            }

# Global instance for DocScanner integration
_docscanner_ollama_rag = None

def get_rag_suggestion(feedback_text: str, sentence_context: str = "",
                      document_type: str = "general", 
                      document_content: str = "") -> Optional[Dict[str, Any]]:
    """
    Global function for DocScanner integration.
    Maintains same interface as Google Gemini version.
    """
    global _docscanner_ollama_rag
    
    if _docscanner_ollama_rag is None:
        _docscanner_ollama_rag = DocScannerOllamaRAG()
    
    return _docscanner_ollama_rag.get_rag_suggestion(
        feedback_text, sentence_context, document_type, document_content
    )

def test_docscanner_ollama():
    """Test function for DocScanner Ollama RAG"""
    print("🤖 DocScanner Ollama RAG Test")
    print("=" * 40)
    
    system = DocScannerOllamaRAG()
    status = system.test_system()
    
    print(f"Status: {status}")
    
    if status["available"]:
        print("✅ Your DocScanner now has local AI!")
        print(f"Model: {status['model']}")
        print(f"Benefits: {' '.join(status['benefits'])}")
        print(f"Sample: {status.get('suggestion_preview', 'N/A')}")
    else:
        print("❌ Setup needed")
        print(f"Issue: {status.get('reason', 'Unknown')}")

if __name__ == "__main__":
    test_docscanner_ollama()
