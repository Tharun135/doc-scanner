"""
Smart RAG Manager - Local Ollama/LlamaIndex AI with unlimited usage
Completely eliminates Google API quotas by using local Llama models.
"""

import logging
import time
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import threading

logger = logging.getLogger(__name__)

class SmartRAGManager:
    """
    Intelligent RAG manager using LOCAL OLLAMA MODELS:
    1. Unlimited usage (no API quotas)
    2. Fast local AI responses
    3. Enhanced caching for even better performance
    4. No external dependencies or costs
    """
    
    def __init__(self):
        self.cache_file = "local_ai_response_cache.json"
        self.response_cache = self._load_response_cache()
        self._lock = threading.Lock()
        self._local_ai_engine = None
        self._ai_initialized = False
        
        # PERFORMANCE MODE: Skip AI for non-critical rules
        self.performance_mode = True  # Enable for faster analysis
        
        # LAZY LOADING: Don't initialize AI engine until actually needed
        logger.info("🚀 Smart RAG Manager ready (AI engine will load on first use)")
    
    def _initialize_local_ai(self):
        """Initialize local Ollama/LlamaIndex AI engine ONLY when needed."""
        if self._ai_initialized:
            return
            
        try:
            logger.info("🤖 Initializing local AI engine on first use...")
            start_time = time.time()
            
            # Import the local AI system
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from llamaindex_ai import get_ai_suggestion, LlamaIndexAISuggestionEngine
            
            self._local_ai_engine = LlamaIndexAISuggestionEngine()
            self._get_ai_suggestion = get_ai_suggestion
            
            init_time = time.time() - start_time
            
            if self._local_ai_engine.is_initialized:
                logger.info(f"✅ Local AI engine initialized in {init_time:.2f}s - UNLIMITED USAGE!")
            else:
                logger.warning(f"⚠️ Local AI engine partial init in {init_time:.2f}s - fallback available")
                
            self._ai_initialized = True
                
        except Exception as e:
            logger.warning(f"❌ Could not initialize local AI engine: {e}")
            self._local_ai_engine = None
            self._get_ai_suggestion = None
            self._ai_initialized = True  # Mark as attempted to prevent retry loops
    
    def _load_response_cache(self) -> Dict:
        """Load cached responses."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load response cache: {e}")
        return {}
    
    def _save_response_cache(self):
        """Save response cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.response_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save response cache: {e}")
    
    def get_cached_response(self, text: str, rule_name: str) -> Optional[str]:
        """Get cached response if available."""
        cache_key = f"{rule_name}:{hash(text)}"
        return self.response_cache.get(cache_key)
    
    def cache_response(self, text: str, rule_name: str, response: str):
        """Cache successful response."""
        cache_key = f"{rule_name}:{hash(text)}"
        self.response_cache[cache_key] = response
        
        # Limit cache size
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            items = list(self.response_cache.items())
            self.response_cache = dict(items[-500:])
        
        self._save_response_cache()
    
    def get_smart_suggestion(self, text: str, rule_name: str, context: str = "") -> tuple[Optional[str], str]:
        """
        Get smart suggestion using LOCAL OLLAMA AI (unlimited usage).
        No fallbacks - AI-only suggestions.
        
        Returns:
            (suggestion, source) where source is 'cache', 'local_ai', or 'ai_error'
        """
        # PERFORMANCE MODE: Only use AI for critical rules
        if self.performance_mode:
            # Expanded critical rules that benefit from AI suggestions
            # Note: These match the actual rule_name parameters passed to check_with_rag
            critical_rules = [
                "passive_voice", "long_sentences", "manual_steps_rewriting", 
                "grammar_issues", "redundant_phrases", "readability_metrics",
                "spelling_checker", "style_guide", "modal_verbs_can_may",
                "cross_references_links", "document_structure", "inclusive_language"
            ]
            if not any(critical in rule_name for critical in critical_rules):
                logger.info(f"Performance mode: Skipping AI for {rule_name}")
                return None, "performance_skip"
        
        # Check cache first for instant response
        cached = self.get_cached_response(text, rule_name)
        if cached:
            return cached, "cache"
        
        # Initialize AI engine only when actually needed (lazy loading)
        if not self._ai_initialized:
            self._initialize_local_ai()
        
        # Use local Ollama AI (NO QUOTAS! UNLIMITED!)
        if self._local_ai_engine and self._get_ai_suggestion:
            try:
                start_time = time.time()
                
                # Create context-aware prompt for the specific rule
                prompt = self._create_rule_specific_prompt(text, rule_name, context)
                
                # Get AI suggestion using local Ollama (correct API)
                suggestion_result = self._get_ai_suggestion(
                    feedback_text=prompt,
                    sentence_context=text,
                    document_type="technical"
                )
                
                elapsed = time.time() - start_time
                
                if suggestion_result and isinstance(suggestion_result, dict):
                    suggestion = suggestion_result.get("suggestion", "")
                    if suggestion and suggestion.strip():
                        # Cache the successful response
                        self.cache_response(text, rule_name, suggestion)
                        logger.info(f"🤖 Local AI suggestion for {rule_name} in {elapsed:.2f}s")
                        return suggestion, "local_ai"
                    else:
                        logger.warning(f"Local AI returned empty suggestion for {rule_name}")
                        return None, "ai_error"
                else:
                    logger.warning(f"Local AI returned invalid result for {rule_name}")
                    return None, "ai_error"
                    
            except Exception as e:
                logger.error(f"Local AI error for {rule_name}: {e}")
                return None, "ai_error"
        else:
            logger.error("Local AI engine not available")
            return None, "ai_error"
    
    def _create_rule_specific_prompt(self, text: str, rule_name: str, context: str = "") -> str:
        """Create optimized prompt for specific rule types."""
        rule_prompts = {
            "passive_voice": f"Convert this passive voice to active voice: '{text}'",
            "long_sentences": f"Break this long sentence into shorter, clearer sentences: '{text}'",
            "technical_terms": f"Improve technical term capitalization and formatting: '{text}'",
            "grammar_issues": f"Fix grammar issues in: '{text}'",
            "style_formatting": f"Improve style and formatting: '{text}'",
        }
        
        base_prompt = rule_prompts.get(rule_name, f"Improve this text for {rule_name}: '{text}'")
        
        if context:
            base_prompt += f" Context: {context}"
            
        return base_prompt
    
    def get_status(self) -> Dict[str, Any]:
        """Get current local AI system status - AI-only, no fallbacks."""
        return {
            "ai_engine_available": self._local_ai_engine is not None,
            "ai_engine_initialized": getattr(self._local_ai_engine, 'is_initialized', False) if self._local_ai_engine else False,
            "ai_init_attempted": self._ai_initialized,
            "cached_responses": len(self.response_cache),
            "quota_limits": "NONE - Unlimited local AI usage! 🚀",
            "fallback_system": "DISABLED - AI-only suggestions",
            "model_info": getattr(self._local_ai_engine, 'model_name', 'Not loaded yet') if self._local_ai_engine else "Lazy loading enabled",
            "loading_strategy": "Lazy loading - AI engine loads on first use for fast startup",
            "suggestion_mode": "AI-ONLY (no rule-based fallbacks)"
        }

# Global manager instance (lazy loaded)
_rag_manager = None

def _get_rag_manager():
    """Get or create the global RAG manager instance (lazy loading)."""
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = SmartRAGManager()
    return _rag_manager

def get_smart_rag_suggestion(text: str, rule_name: str, context: str = "") -> tuple[Optional[str], str]:
    """
    Get AI suggestion using LOCAL OLLAMA MODEL (unlimited usage, AI-only).
    
    Args:
        text: Text to analyze
        rule_name: Name of the rule
        context: Additional context for better suggestions
    
    Returns:
        (suggestion, source) where source indicates where suggestion came from:
        - 'cache': Instant cached response
        - 'local_ai': Fresh AI response from local Ollama
        - 'ai_error': AI system failed (no fallbacks)
    """
    return _get_rag_manager().get_smart_suggestion(text, rule_name, context)

def get_rag_status() -> Dict[str, Any]:
    """Get local AI system status - NO QUOTAS, UNLIMITED USAGE, AI-ONLY! 🚀"""
    return _get_rag_manager().get_status()

def clear_local_ai_cache():
    """Clear all cached AI responses."""
    manager = _get_rag_manager()
    manager.response_cache.clear()
    manager._save_response_cache()
    logger.info("Local AI response cache cleared")

def get_cache_stats() -> Dict[str, Any]:
    """Get local AI cache statistics."""
    manager = _get_rag_manager()
    return {
        "cached_responses": len(manager.response_cache),
        "ai_engine_available": manager._local_ai_engine is not None,
        "unlimited_usage": True,
        "quota_free": "✅ No quotas with local Ollama!",
        "fallback_system": "❌ Disabled - AI-only mode"
    }
