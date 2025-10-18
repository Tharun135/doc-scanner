"""
Enhanced AI Suggestion System - Multi-layered Architecture
==========================================================

This module implements a robust 4-layer AI suggestion system:
1. Smart Rule Engine (regex-based patterns)
2. RAG Context Retrieval (ChromaDB embeddings) 
3. LLM Integration (OpenAI/Ollama with controlled prompts)
4. Confidence & Quality Filter (similarity + grammar scoring)

Architecture Flow:
Sentence → Smart Rules → RAG Context → LLM Rewriter → Quality Filter → Final Suggestion
"""

import os
import re
import logging
import json
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports with graceful fallbacks
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available - RAG context disabled")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - LLM suggestions disabled")

try:
    import language_tool_python
    GRAMMAR_TOOL_AVAILABLE = True
except ImportError:
    GRAMMAR_TOOL_AVAILABLE = False
    logger.warning("Language Tool not available - grammar scoring disabled")

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


@dataclass
class AIConfig:
    """Configuration for the AI suggestion system."""
    # RAG Settings
    chroma_path: str = "./chroma_db"
    collection_name: str = "docscanner_examples"
    rag_top_k: int = 3
    
    # LLM Settings
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.4
    openai_max_tokens: int = 100
    ollama_model: str = "mistral"
    ollama_endpoint: str = "http://localhost:11434"
    
    # Quality Settings
    min_similarity_threshold: float = 0.1  # Too similar = unchanged
    max_similarity_threshold: float = 0.9  # Too different = wrong meaning
    require_grammar_improvement: bool = True
    
    # Performance Settings
    enable_rag: bool = True
    enable_llm: bool = True
    enable_quality_filter: bool = True


class ChromaDBRetriever:
    """Handles context retrieval from ChromaDB."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = None
        self.collection = None
        
        if CHROMADB_AVAILABLE:
            try:
                self.client = chromadb.Client(Settings(
                    persist_directory=config.chroma_path
                ))
                self.collection = self._get_or_create_collection()
                logger.info("✅ ChromaDB initialized successfully")
            except Exception as e:
                logger.error(f"ChromaDB initialization failed: {e}")
                self.client = None
    
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            return self.client.get_collection(self.config.collection_name)
        except:
            # Create collection with sample data
            collection = self.client.create_collection(self.config.collection_name)
            self._populate_sample_data(collection)
            return collection
    
    def _populate_sample_data(self, collection):
        """Add sample writing examples to the collection."""
        sample_examples = [
            {
                "id": "passive_1",
                "document": "The configuration options are displayed → The system displays the configuration options.",
                "metadata": {"type": "passive_voice", "category": "ui_description"}
            },
            {
                "id": "passive_2", 
                "document": "The file was created by the system → The system created the file.",
                "metadata": {"type": "passive_voice", "category": "system_action"}
            },
            {
                "id": "adverb_1",
                "document": "Configure the credentials accordingly → Configure the credentials as specified.",
                "metadata": {"type": "adverb_replacement", "category": "instructions"}
            },
            {
                "id": "conciseness_1",
                "document": "In order to configure the system → To configure the system.",
                "metadata": {"type": "conciseness", "category": "instructions"}
            },
            {
                "id": "clarity_1",
                "document": "Click on the button → Click the button.",
                "metadata": {"type": "clarity", "category": "ui_actions"}
            }
        ]
        
        try:
            collection.add(
                documents=[ex["document"] for ex in sample_examples],
                ids=[ex["id"] for ex in sample_examples],
                metadatas=[ex["metadata"] for ex in sample_examples]
            )
            logger.info("Sample data populated in ChromaDB")
        except Exception as e:
            logger.error(f"Failed to populate sample data: {e}")
    
    def get_contextual_examples(self, query_text: str) -> List[str]:
        """Retrieve top contextual examples from ChromaDB."""
        if not self.collection:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query_text], 
                n_results=self.config.rag_top_k
            )
            examples = results.get("documents", [[]])[0]
            logger.info(f"Retrieved {len(examples)} contextual examples")
            return examples
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            return []


class LLMIntegrator:
    """Handles LLM-based suggestions with multiple providers."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.openai_client = None
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if openai.api_key:
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
            else:
                logger.warning("OpenAI API key not found")
    
    def generate_llm_suggestion(self, sentence: str, context_examples: List[str] = None) -> Optional[str]:
        """Generate rewrite using available LLM provider."""
        
        # Try OpenAI first
        if self.openai_client:
            return self._generate_openai_suggestion(sentence, context_examples)
        
        # Fallback to Ollama if available
        if OLLAMA_AVAILABLE:
            return self._generate_ollama_suggestion(sentence, context_examples)
        
        logger.warning("No LLM provider available")
        return None
    
    def _generate_openai_suggestion(self, sentence: str, context_examples: List[str] = None) -> Optional[str]:
        """Generate suggestion using OpenAI."""
        prompt = self._build_prompt(sentence, context_examples)
        
        try:
            response = self.openai_client.ChatCompletion.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens
            )
            suggestion = response.choices[0].message["content"].strip()
            logger.info("✅ OpenAI suggestion generated")
            return suggestion
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _generate_ollama_suggestion(self, sentence: str, context_examples: List[str] = None) -> Optional[str]:
        """Generate suggestion using Ollama."""
        prompt = self._build_prompt(sentence, context_examples)
        
        try:
            payload = {
                "model": self.config.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.openai_temperature,
                    "num_predict": self.config.openai_max_tokens
                }
            }
            
            response = requests.post(
                f"{self.config.ollama_endpoint}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion = result.get("response", "").strip()
                logger.info("✅ Ollama suggestion generated")
                return suggestion
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return None
    
    def _build_prompt(self, sentence: str, context_examples: List[str] = None) -> str:
        """Build optimized prompt for LLM rewriting."""
        context_str = ""
        if context_examples:
            context_str = f"\n\nContext examples:\n" + "\n".join([f"- {ex}" for ex in context_examples])
        
        return f"""You are an expert technical writing assistant for software documentation.

Task: Rewrite the following sentence to improve clarity, conciseness, and correctness while maintaining the original meaning and professional tone suitable for user manuals.

Guidelines:
- Use active voice when possible
- Remove unnecessary words  
- Use clear, direct language
- Maintain technical accuracy
- Keep the same meaning{context_str}

Original: "{sentence}"

Improved version:"""


class QualityFilter:
    """Filters low-quality suggestions using multiple metrics."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.grammar_tool = None
        
        if GRAMMAR_TOOL_AVAILABLE:
            try:
                self.grammar_tool = language_tool_python.LanguageTool('en-US')
                logger.info("✅ Grammar tool initialized")
            except Exception as e:
                logger.error(f"Grammar tool initialization failed: {e}")
    
    def validate_suggestion(self, original: str, suggestion: str) -> Optional[str]:
        """Validate suggestion quality using multiple criteria."""
        if not suggestion or len(suggestion.strip()) == 0:
            logger.debug("Rejected: Empty suggestion")
            return None
        
        suggestion = suggestion.strip()
        
        # Check similarity bounds
        similarity = self._get_similarity(original, suggestion)
        if similarity < self.config.min_similarity_threshold:
            logger.debug(f"Rejected: Too different (similarity: {similarity:.2f})")
            return None
        
        if similarity > self.config.max_similarity_threshold:
            logger.debug(f"Rejected: Too similar (similarity: {similarity:.2f})")
            return None
        
        # Check grammar improvement
        if self.config.require_grammar_improvement and self.grammar_tool:
            if not self._grammar_improved(original, suggestion):
                logger.debug("Rejected: Grammar not improved")
                return None
        
        # Check for common LLM artifacts
        if self._has_llm_artifacts(suggestion):
            logger.debug("Rejected: Contains LLM artifacts")
            return None
        
        logger.info(f"✅ Suggestion validated (similarity: {similarity:.2f})")
        return suggestion
    
    def _get_similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def _grammar_improved(self, original: str, suggestion: str) -> bool:
        """Check if grammar score improved."""
        if not self.grammar_tool:
            return True  # Skip check if tool unavailable
        
        try:
            orig_score = self._grammar_score(original)
            sugg_score = self._grammar_score(suggestion)
            return sugg_score >= orig_score
        except:
            return True  # Skip on error
    
    def _grammar_score(self, text: str) -> float:
        """Calculate normalized grammar score (0-1, higher is better)."""
        matches = self.grammar_tool.check(text)
        words = len(text.split())
        if words == 0:
            return 0
        return max(0, 1 - len(matches) / words)
    
    def _has_llm_artifacts(self, suggestion: str) -> bool:
        """Check for common LLM response artifacts."""
        artifacts = [
            "here's a rewrite", "improved version", "better phrasing",
            "rewritten sentence", "corrected version", "revised text"
        ]
        suggestion_lower = suggestion.lower()
        return any(artifact in suggestion_lower for artifact in artifacts)


class SmartRuleEngine:
    """Advanced rule-based suggestion system with JSON rules."""
    
    def __init__(self):
        self.rules = self._load_rules()
        logger.info(f"✅ Loaded {len(self.rules)} smart rules")
    
    def _load_rules(self) -> List[Dict]:
        """Load rules from JSON file or use defaults."""
        try:
            with open("smart_rules.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_rules()
    
    def _get_default_rules(self) -> List[Dict]:
        """Default rule set for common writing issues."""
        return [
            {
                "id": "passive_are_displayed",
                "pattern": r"\bare displayed\b",
                "replacement": "appear",
                "explanation": "Converted passive voice to active",
                "category": "passive_voice"
            },
            {
                "id": "passive_is_displayed", 
                "pattern": r"\bis displayed\b",
                "replacement": "appears",
                "explanation": "Converted passive voice to active",
                "category": "passive_voice"
            },
            {
                "id": "click_on_fix",
                "pattern": r"\bclick on\b",
                "replacement": "click",
                "explanation": "Simplified UI instruction",
                "category": "ui_clarity"
            },
            {
                "id": "accordingly_vague",
                "pattern": r"\baccordingly\b",
                "replacement": "as specified",
                "explanation": "Replaced vague term with specific instruction",
                "category": "clarity"
            },
            {
                "id": "in_order_to_wordiness",
                "pattern": r"\bin order to\b",
                "replacement": "to",
                "explanation": "Removed unnecessary wordiness",
                "category": "conciseness"
            },
            {
                "id": "due_to_fact",
                "pattern": r"\bdue to the fact that\b",
                "replacement": "because",
                "explanation": "Simplified wordy expression",
                "category": "conciseness"
            }
        ]
    
    def apply_smart_rules(self, sentence: str) -> Optional[Dict[str, Any]]:
        """Apply smart rules and return first match with details."""
        for rule in self.rules:
            pattern = rule["pattern"]
            if re.search(pattern, sentence, re.IGNORECASE):
                suggestion = re.sub(pattern, rule["replacement"], sentence, flags=re.IGNORECASE)
                
                return {
                    "suggestion": suggestion,
                    "ai_answer": f"{rule['explanation']}. This improves {rule['category']} in technical documentation.",
                    "confidence": "high",
                    "method": "smart_rule_based",
                    "sources": [f"Rule: {rule['id']}"],
                    "original_sentence": sentence,
                    "success": True
                }
        
        return None


class EnhancedAISuggestionSystem:
    """Main AI suggestion system combining all layers."""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        
        # Initialize all components
        self.rule_engine = SmartRuleEngine()
        self.rag_retriever = ChromaDBRetriever(self.config) if self.config.enable_rag else None
        self.llm_integrator = LLMIntegrator(self.config) if self.config.enable_llm else None
        self.quality_filter = QualityFilter(self.config) if self.config.enable_quality_filter else None
        
        logger.info("✅ Enhanced AI Suggestion System initialized")
    
    def generate_ai_suggestion(
        self, 
        sentence: str,
        feedback_text: str = "",
        document_type: str = "general",
        writing_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI suggestion using multi-layer approach.
        
        Flow: Smart Rules → RAG Context → LLM → Quality Filter
        """
        logger.info(f"Processing: '{sentence[:50]}...'")
        
        # Layer 1: Smart Rule Engine
        rule_suggestion = self.rule_engine.apply_smart_rules(sentence)
        if rule_suggestion:
            validated = self._validate_if_enabled(sentence, rule_suggestion["suggestion"])
            if validated:
                rule_suggestion["suggestion"] = validated
                logger.info("✅ Using smart rule suggestion")
                return rule_suggestion
        
        # Layer 2: RAG Context + LLM Integration
        if self.rag_retriever and self.llm_integrator:
            context_examples = self.rag_retriever.get_contextual_examples(sentence)
            llm_suggestion = self.llm_integrator.generate_llm_suggestion(sentence, context_examples)
            
            validated = self._validate_if_enabled(sentence, llm_suggestion)
            if validated:
                logger.info("✅ Using RAG + LLM suggestion")
                return {
                    "suggestion": validated,
                    "ai_answer": f"Improved based on contextual analysis and language model processing. Enhanced for clarity and technical writing standards.",
                    "confidence": "high",
                    "method": "rag_llm_enhanced",
                    "sources": [f"Context examples: {len(context_examples)}", "LLM processing"],
                    "original_sentence": sentence,
                    "success": True
                }
        
        # Layer 3: LLM-only fallback
        elif self.llm_integrator:
            llm_suggestion = self.llm_integrator.generate_llm_suggestion(sentence)
            validated = self._validate_if_enabled(sentence, llm_suggestion)
            if validated:
                logger.info("✅ Using LLM-only suggestion")
                return {
                    "suggestion": validated,
                    "ai_answer": "Improved using language model analysis for better clarity and grammar.",
                    "confidence": "medium",
                    "method": "llm_only",
                    "sources": ["Language model processing"],
                    "original_sentence": sentence,
                    "success": True
                }
        
        # Layer 4: Fallback - provide guidance
        logger.info("⚠️ Using fallback guidance")
        return {
            "suggestion": sentence,
            "ai_answer": f"Consider revising this sentence for better clarity and conciseness. Focus on using active voice, removing unnecessary words, and ensuring clear meaning.",
            "confidence": "low",
            "method": "guidance_fallback",
            "sources": ["General writing guidelines"],
            "original_sentence": sentence,
            "success": False
        }
    
    def _validate_if_enabled(self, original: str, suggestion: str) -> Optional[str]:
        """Validate suggestion if quality filter is enabled."""
        if self.quality_filter and suggestion:
            return self.quality_filter.validate_suggestion(original, suggestion)
        return suggestion


# Global instance for the application
_ai_system = None

def get_enhanced_ai_suggestion(
    feedback_text: str,
    sentence_context: str = "",
    document_type: str = "general",
    writing_goals: Optional[List[str]] = None,
    document_content: str = "",
    option_number: int = 1,
    issue: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main entry point for enhanced AI suggestions.
    Compatible with existing DocScanner interface.
    """
    global _ai_system
    
    if _ai_system is None:
        _ai_system = EnhancedAISuggestionSystem()
    
    try:
        result = _ai_system.generate_ai_suggestion(
            sentence=sentence_context,
            feedback_text=feedback_text,
            document_type=document_type,
            writing_goals=writing_goals or []
        )
        return result
        
    except Exception as e:
        logger.error(f"AI suggestion generation failed: {e}")
        return {
            "suggestion": sentence_context,
            "ai_answer": f"Unable to generate suggestion: {str(e)}",
            "confidence": "low",
            "method": "error_fallback",
            "sources": [],
            "original_sentence": sentence_context,
            "success": False
        }


if __name__ == "__main__":
    # Test the system
    test_sentences = [
        "The configuration options are displayed.",
        "Click on the button to proceed.",
        "Configure the credentials accordingly.",
        "In order to complete the setup, you need to restart the system."
    ]
    
    print("🧪 Testing Enhanced AI Suggestion System")
    print("=" * 60)
    
    for sentence in test_sentences:
        print(f"\n📝 Input: {sentence}")
        result = get_enhanced_ai_suggestion(
            feedback_text="Improve this sentence",
            sentence_context=sentence
        )
        print(f"✨ Output: {result['suggestion']}")
        print(f"🔧 Method: {result['method']}")
        print(f"🎯 Confidence: {result['confidence']}")
