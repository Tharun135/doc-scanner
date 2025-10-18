# enhanced_rag/enhanced_rag_system.py
"""
Complete enhanced RAG system integrating all improvements:
- Enhanced chunking with metadata
- Hybrid retrieval (semantic + BM25)
- Constrained prompting 
- Performance optimization
- Evaluation metrics

This is the main integration class that brings everything together.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
import requests
import json
from functools import lru_cache

from .enhanced_vectorstore import EnhancedVectorStore, get_enhanced_store
from .hybrid_retrieval import RetrievalResult
from .rule_specific_corrections import get_rule_specific_correction, EnhancedRulePrompts
from .comprehensive_rule_engine import get_comprehensive_correction, DocumentType
from .rag_prompt_templates import (
    EnhancedRAGPrompts, 
    RAGResponseFormatter, 
    RAGContext
)

logger = logging.getLogger(__name__)

class EnhancedRAGSystem:
    """
    Complete enhanced RAG system with all improvements integrated.
    Drop-in replacement for existing RAG with better performance and accuracy.
    """
    
    def __init__(self,
                 collection_name: str = "docscanner_enhanced",
                 ollama_url: str = "http://localhost:11434",
                 model_name: str = "phi3:mini",
                 hybrid_alpha: float = 0.6,
                 max_context_chunks: int = 3,
                 timeout_seconds: float = 2.0):
        """
        Initialize enhanced RAG system.
        
        Args:
            collection_name: ChromaDB collection name
            ollama_url: Ollama API URL
            model_name: Ollama model name for generation
            hybrid_alpha: Weight for semantic vs BM25 scores
            max_context_chunks: Maximum chunks to pass to LLM
            timeout_seconds: Timeout for LLM calls
        """
        self.collection_name = collection_name
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.max_context_chunks = max_context_chunks
        self.timeout_seconds = timeout_seconds
        
        # Initialize components
        self.vector_store = get_enhanced_store(collection_name)
        self.vector_store.hybrid_retriever.alpha = hybrid_alpha
        
        # Performance tracking
        self.metrics = {
            "total_queries": 0,
            "successful_responses": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "fallback_uses": 0
        }
        
        logger.info(f"✅ Enhanced RAG system initialized with {model_name}")
    
    def get_rag_suggestion(self,
                          feedback_text: str,
                          sentence_context: str = "",
                          document_type: str = "general",
                          document_content: str = "",
                          rule_id: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Main entry point for RAG suggestions with enhanced processing.
        
        Args:
            feedback_text: Description of the writing issue
            sentence_context: The problematic sentence
            document_type: Type of document (technical, general, etc.)
            document_content: Full document content for context
            rule_id: ID of the rule that was violated
        
        Returns:
            Enhanced suggestion with sources and confidence
        """
        start_time = time.time()
        self.metrics["total_queries"] += 1
        
        try:
            # Step 1: Enhanced retrieval with hybrid search
            query_text = self._format_rag_query(feedback_text, sentence_context, document_type)
            
            # Apply smart filtering based on document type and context
            product_filter = self._infer_product_from_context(document_content, document_type)
            
            retrieval_results = self.vector_store.query_enhanced(
                query_text=query_text,
                n_results=self.max_context_chunks + 2,  # Get a few extra for filtering
                use_hybrid=True,
                product_filter=product_filter
            )
            
            # Step 2: Convert to RAG contexts
            rag_contexts = self._convert_to_rag_contexts(retrieval_results)
            
            # Step 3: Generate response with constrained prompting
            response = self._generate_constrained_response(
                flagged_sentence=sentence_context,
                rule_id=rule_id,
                retrieved_chunks=rag_contexts[:self.max_context_chunks]
            )
            
            # Step 4: Format and return enhanced response
            if response:
                self.metrics["successful_responses"] += 1
                
                # Calculate confidence based on retrieval quality
                confidence = self._calculate_confidence_enhanced(
                    retrieval_results, 
                    query_text, 
                    response
                )
                
                # Format sources with metadata
                sources = RAGResponseFormatter.format_sources(rag_contexts)
                
                formatted_response = RAGResponseFormatter.format_suggestion(
                    original_sentence=sentence_context,
                    correction=response.get("correction", ""),
                    explanation=response.get("reason", ""),
                    confidence=confidence,
                    sources=sources,
                    method="enhanced_rag"
                )
                
                # Update timing metrics
                response_time = time.time() - start_time
                self._update_response_time_metric(response_time)
                
                return formatted_response
            else:
                # Fallback to deterministic response
                self.metrics["fallback_uses"] += 1
                return self._create_enhanced_fallback(
                    feedback_text, 
                    sentence_context, 
                    rule_id
                )
                
        except Exception as e:
            logger.error(f"❌ Enhanced RAG failed: {e}")
            self.metrics["fallback_uses"] += 1
            return self._create_enhanced_fallback(feedback_text, sentence_context, rule_id)
    
    def _format_rag_query(self, 
                         feedback_text: str, 
                         sentence_context: str, 
                         document_type: str) -> str:
        """Enhanced query formatting with context awareness"""
        # Extract key terms from feedback and sentence
        key_terms = []
        
        # Add feedback terms
        if feedback_text:
            key_terms.extend(feedback_text.lower().split())
        
        # Add important words from sentence (filter out common words)
        if sentence_context:
            sentence_words = [w for w in sentence_context.lower().split() 
                            if len(w) > 3 and w not in {'this', 'that', 'with', 'from', 'they', 'were', 'been', 'have'}]
            key_terms.extend(sentence_words[:5])  # Top 5 content words
        
        # Add document type context
        if document_type != "general":
            key_terms.append(document_type)
        
        # Create focused query
        query = " ".join(key_terms[:10])  # Limit to 10 terms for focus
        
        return query
    
    def _infer_product_from_context(self, 
                                   document_content: str, 
                                   document_type: str) -> Optional[str]:
        """Infer product filter from document context"""
        if not document_content:
            return None
            
        content_lower = document_content.lower()
        
        # Simple product detection based on keywords
        if any(term in content_lower for term in ['azure', 'microsoft', 'office']):
            return 'microsoft'
        elif any(term in content_lower for term in ['docscanner', 'doc-scanner']):
            return 'docscanner'
        elif 'technical' in document_type.lower():
            return 'technical'
        
        return None
    
    def _convert_to_rag_contexts(self, 
                                retrieval_results: List[Dict[str, Any]]) -> List[RAGContext]:
        """Convert retrieval results to RAG contexts"""
        contexts = []
        
        for i, result in enumerate(retrieval_results):
            # Use hybrid score if available, otherwise use semantic score
            score = result.get('hybrid_score', result.get('distance', 0))
            if 'distance' in result:  # Convert distance to similarity
                score = max(0, 1.0 - score)
            
            context = RAGContext(
                chunk_id=result['id'],
                text=result['text'],
                metadata=result['metadata'],
                score=score,
                source_label=f"[{i+1}]"
            )
            contexts.append(context)
        
        return contexts
    
    def _generate_constrained_response(self,
                                     flagged_sentence: str,
                                     rule_id: str,
                                     retrieved_chunks: List[RAGContext]) -> Optional[Dict[str, str]]:
        """Generate response using constrained prompting with comprehensive rule engine"""
        try:
            # For simple rule types, try comprehensive rule engine first
            simple_rules = ["capitalization", "click-on", "adverb-usage", "punctuation"]
            
            if any(simple_rule in rule_id.lower() for simple_rule in simple_rules):
                # Try comprehensive rule engine for intelligent corrections
                comprehensive_result = get_comprehensive_correction(
                    text=flagged_sentence,
                    rule_id=rule_id,
                    document_content="",  # Could be enhanced with full document
                    document_type="general"
                )
                
                if (comprehensive_result['confidence'] > 0.7 and 
                    comprehensive_result['corrected'] != flagged_sentence):
                    return {
                        "correction": comprehensive_result['corrected'],
                        "reason": comprehensive_result['explanation'],
                        "source": f"comprehensive rule engine ({comprehensive_result['method']})"
                    }
            
            # For complex rules or when comprehensive engine doesn't have high confidence, use enhanced prompting
            if retrieved_chunks and len(retrieved_chunks) > 0:
                # Use standard constrained prompting with context
                prompt = EnhancedRAGPrompts.build_constrained_prompt(
                    flagged_sentence=flagged_sentence,
                    rule_id=rule_id,
                    retrieved_chunks=retrieved_chunks
                )
            else:
                # Use rule-specific prompting when no good context available
                prompt = EnhancedRulePrompts.get_rule_specific_prompt(
                    flagged_sentence, rule_id
                )
            
            # Call Ollama with optimized settings
            response = self._call_ollama_optimized(prompt)
            
            if response:
                # Parse structured response
                parsed = EnhancedRAGPrompts.parse_llm_response(response)
                return parsed
            
        except Exception as e:
            logger.error(f"❌ Constrained response generation failed: {e}")
        
        return None
    
    @lru_cache(maxsize=200)
    def _call_ollama_optimized(self, prompt: str) -> Optional[str]:
        """Optimized Ollama call with caching and fast timeout"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.2,     # Lower for consistency
                        'top_p': 0.8,
                        'num_predict': 50,      # Shorter responses
                        'num_ctx': 1024,        # Moderate context window
                        'repeat_penalty': 1.1
                    }
                },
                timeout=self.timeout_seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
                
        except requests.exceptions.Timeout:
            logger.warning(f"⚡ Ollama timeout ({self.timeout_seconds}s)")
        except requests.exceptions.ConnectionError:
            logger.warning("🔌 Ollama not accessible")
        except Exception as e:
            logger.error(f"❌ Ollama call failed: {e}")
        
        return None
    
    def _calculate_confidence_enhanced(self,
                                     retrieval_results: List[Dict[str, Any]],
                                     query: str,
                                     response: Dict[str, str]) -> str:
        """Enhanced confidence calculation"""
        if not retrieval_results:
            return "very_low"
        
        # Get best score
        best_result = retrieval_results[0]
        best_score = best_result.get('hybrid_score', best_result.get('distance', 0))
        
        if 'distance' in best_result:
            best_score = max(0, 1.0 - best_score)
        
        # Check for exact matches
        has_exact_match = any(
            query.lower() in result['text'].lower() 
            for result in retrieval_results[:3]
        )
        
        # Check response quality
        has_guidance = response.get('has_guidance', True)
        has_source = bool(response.get('source', ''))
        
        # Calculate confidence
        confidence_score = 0
        
        if best_score > 0.8:
            confidence_score += 3
        elif best_score > 0.6:
            confidence_score += 2
        elif best_score > 0.4:
            confidence_score += 1
        
        if has_exact_match:
            confidence_score += 2
        
        if has_guidance and has_source:
            confidence_score += 2
        
        if len(retrieval_results) >= 2:
            confidence_score += 1
        
        # Map to confidence levels
        if confidence_score >= 6:
            return "high"
        elif confidence_score >= 4:
            return "medium"
        elif confidence_score >= 2:
            return "low"
        else:
            return "very_low"
    
    def _create_enhanced_fallback(self,
                                feedback_text: str,
                                sentence_context: str,
                                rule_id: str) -> Dict[str, Any]:
        """Create enhanced fallback response using comprehensive rule engine"""
        
        # First try comprehensive rule engine for intelligent corrections
        comprehensive_result = get_comprehensive_correction(
            text=sentence_context,
            rule_id=rule_id,
            document_content=feedback_text,  # Use feedback as context hint
            document_type="general"
        )
        
        # If comprehensive engine provided a good correction, use it
        if (comprehensive_result['confidence'] > 0.5 and 
            comprehensive_result['corrected'] != sentence_context):
            
            return RAGResponseFormatter.format_suggestion(
                original_sentence=sentence_context,
                correction=comprehensive_result['corrected'],
                explanation=comprehensive_result['explanation'],
                confidence=f"{comprehensive_result['confidence']:.1f}",  # Convert to string
                sources=[],
                method=comprehensive_result['method']
            )
        
        # Fallback to rule-specific correction
        rule_specific_correction = get_rule_specific_correction(sentence_context, rule_id, feedback_text)
        
        # If the rule-specific correction made a meaningful change, use it
        if rule_specific_correction != sentence_context and rule_specific_correction.strip():
            return RAGResponseFormatter.format_suggestion(
                original_sentence=sentence_context,
                correction=rule_specific_correction,
                explanation=f"Applied {rule_id} rule using targeted correction logic.",
                confidence="medium",
                sources=[],
                method="rule_specific_correction"
            )
        
        # Fallback to specialized prompt for this rule type
        specialized_prompt = EnhancedRulePrompts.get_rule_specific_prompt(
            sentence_context, rule_id
        )
        
        # Try quick Ollama call with specialized prompt
        correction = self._call_ollama_optimized(specialized_prompt)
        
        if not correction or correction.strip() == sentence_context.strip():
            # Final fallback to deterministic correction
            correction = self._deterministic_correction(sentence_context, rule_id, feedback_text)
        
        return RAGResponseFormatter.format_suggestion(
            original_sentence=sentence_context,
            correction=correction,
            explanation=f"Applied {rule_id} rule (enhanced fallback mode)",
            confidence="low",
            sources=[],
            method="enhanced_fallback"
        )
    
    def _deterministic_correction(self, sentence: str, rule_id: str, feedback_text: str = "") -> str:
        """Enhanced deterministic corrections using rule-specific logic"""
        
        # Use the rule-specific correction as primary method
        corrected = get_rule_specific_correction(sentence, rule_id, feedback_text)
        
        # If rule-specific correction worked, return it
        if corrected != sentence and corrected.strip():
            return corrected
        
        # Legacy fallback corrections for backwards compatibility
        sentence = sentence.strip()
        
        if rule_id == "passive-voice":
            # Simple passive to active conversion attempts
            if "was " in sentence.lower():
                return sentence.replace("was ", "").replace("by the", "the")
            elif "is " in sentence.lower() and " by " in sentence.lower():
                parts = sentence.split(" by ")
                if len(parts) == 2:
                    return f"{parts[1].strip()} {parts[0].replace('is ', '').strip()}"
        
        elif rule_id == "adverb-usage":
            # Remove common adverbs
            adverbs = ["really", "very", "quite", "easily", "simply", "basically"]
            result = sentence
            for adverb in adverbs:
                result = result.replace(f" {adverb} ", " ").replace(f" {adverb.title()} ", " ")
            return result.strip()
        
        elif rule_id == "click-on":
            return sentence.replace("click on", "click").replace("Click on", "Click")
        
        # Enhanced deterministic corrections based on feedback text
        elif "capital letter" in feedback_text.lower() or "sentence case" in feedback_text.lower():
            # Fix capitalization
            if sentence and sentence[0].islower():
                return sentence[0].upper() + sentence[1:]
            return sentence
            
        elif "passive voice" in feedback_text.lower():
            # Enhanced passive voice correction
            if " is uploaded by " in sentence:
                return sentence.replace(" is uploaded by ", " uploads ")
            elif " was created by " in sentence:
                return sentence.replace(" was created by ", " created ")
            elif " is " in sentence and " by " in sentence:
                # Generic passive to active conversion
                parts = sentence.split(" by ")
                if len(parts) == 2:
                    subject = parts[1].strip().rstrip('.')
                    predicate = parts[0].replace(" is ", " ").replace(" was ", " ").strip()
                    return f"{subject} {predicate}."
        
        elif "long sentence" in feedback_text.lower() or "shorter sentences" in feedback_text.lower():
            # Break long sentences at natural points
            if len(sentence) > 80:
                # Try to split at conjunctions
                if " and " in sentence:
                    parts = sentence.split(" and ", 1)
                    return f"{parts[0].strip()}. {parts[1].strip().capitalize()}"
                elif ". " in sentence:
                    return sentence  # Already has multiple sentences
                elif ", " in sentence:
                    # Split at comma if sentence is very long
                    parts = sentence.split(", ")
                    if len(parts) >= 3:
                        mid_point = len(parts) // 2
                        part1 = ", ".join(parts[:mid_point]).strip()
                        part2 = ", ".join(parts[mid_point:]).strip()
                        return f"{part1}. {part2.capitalize()}"
        
        # Only use "Improved:" prefix if no specific correction was found
        return f"Improved: {sentence}"  # Generic fallback
    
    def _update_response_time_metric(self, response_time: float):
        """Update running average of response times"""
        total_queries = self.metrics["total_queries"]
        current_avg = self.metrics["avg_response_time"]
        
        # Running average calculation
        new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
        self.metrics["avg_response_time"] = new_avg
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            "performance_metrics": self.metrics,
            "vector_store_stats": vector_stats,
            "configuration": {
                "model_name": self.model_name,
                "collection_name": self.collection_name,
                "max_context_chunks": self.max_context_chunks,
                "timeout_seconds": self.timeout_seconds,
                "hybrid_alpha": self.vector_store.hybrid_retriever.alpha
            }
        }
    
    def evaluate_on_test_set(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the system on a test set for performance measurement.
        
        Args:
            test_cases: List of test cases with 'sentence', 'rule_id', and expected 'correction'
        
        Returns:
            Evaluation metrics
        """
        results = {
            "total_cases": len(test_cases),
            "successful_responses": 0,
            "high_confidence": 0,
            "response_times": [],
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0, "very_low": 0}
        }
        
        for test_case in test_cases:
            start_time = time.time()
            
            response = self.get_rag_suggestion(
                feedback_text=f"{test_case['rule_id']} issue",
                sentence_context=test_case['sentence'],
                rule_id=test_case['rule_id']
            )
            
            response_time = time.time() - start_time
            results["response_times"].append(response_time)
            
            if response:
                results["successful_responses"] += 1
                confidence = response.get("confidence", "very_low")
                results["confidence_distribution"][confidence] += 1
                
                if confidence == "high":
                    results["high_confidence"] += 1
        
        # Calculate summary stats
        if results["response_times"]:
            results["avg_response_time"] = sum(results["response_times"]) / len(results["response_times"])
            results["success_rate"] = results["successful_responses"] / results["total_cases"]
            results["high_confidence_rate"] = results["high_confidence"] / results["total_cases"]
        
        return results


# Factory function for easy integration
def get_enhanced_rag_system(collection_name: str = None) -> EnhancedRAGSystem:
    """Factory function to get enhanced RAG system"""
    if collection_name is None:
        collection_name = "docscanner_enhanced"
    
    return EnhancedRAGSystem(collection_name=collection_name)


# Example usage and testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Enhanced RAG System")
    print("=" * 50)
    
    # Initialize system
    rag_system = get_enhanced_rag_system()
    
    # Test with sample queries
    test_cases = [
        {
            "sentence": "The file was created by the system automatically.",
            "rule_id": "passive-voice",
            "feedback": "passive voice detected"
        },
        {
            "sentence": "You can easily click on the button to continue.",
            "rule_id": "adverb-usage",
            "feedback": "unnecessary adverb usage"
        },
        {
            "sentence": "Simply click on the Save button.",
            "rule_id": "click-on",
            "feedback": "click on usage"
        }
    ]
    
    print("Running test cases...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {test_case['sentence']}")
        print(f"Rule: {test_case['rule_id']}")
        
        response = rag_system.get_rag_suggestion(
            feedback_text=test_case['feedback'],
            sentence_context=test_case['sentence'],
            rule_id=test_case['rule_id']
        )
        
        if response:
            print(f"Correction: {response.get('suggested_correction', 'N/A')}")
            print(f"Confidence: {response.get('confidence', 'N/A')}")
            print(f"Method: {response.get('method', 'N/A')}")
            print(f"Sources: {len(response.get('sources', []))}")
        else:
            print("No response generated")
    
    # Get system metrics
    print(f"\n📊 System Metrics:")
    metrics = rag_system.get_system_metrics()
    print(json.dumps(metrics, indent=2))
