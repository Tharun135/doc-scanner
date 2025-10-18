# enhanced_rag/advanced_integration.py
"""
Advanced RAG integration system that brings together all improvements:
- Advanced semantic chunking
- High-quality embeddings
- Hybrid retrieval with re-ranking
- Structured prompting with style guides
- Feedback collection and adaptation
- Performance monitoring and caching

This is the main integration point that replaces the existing RAG system.
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import sqlite3

# Optional Redis for caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from .advanced_chunking import AdvancedSemanticChunker, EnhancedChunk
from .advanced_embeddings import AdvancedEmbeddingManager, get_embedding_manager
from .advanced_retrieval import AdvancedHybridRetriever, AdvancedRetrievalResult
from .advanced_prompts import AdvancedPromptManager, get_prompt_manager
from .feedback_evaluation import FeedbackEvaluationSystem, UserFeedback, get_feedback_system

logger = logging.getLogger(__name__)


@dataclass
class AdvancedRAGConfig:
    """Configuration for the advanced RAG system."""
    # Chunking settings
    chunk_target_size: int = 500
    chunk_min_size: int = 300
    chunk_max_size: int = 700
    chunk_overlap: int = 75
    
    # Embedding settings
    embedding_provider: str = "auto"  # 'openai', 'cohere', 'sentence_transformers', 'ollama', 'auto'
    embedding_model: Optional[str] = None
    
    # Retrieval settings
    semantic_weight: float = 0.6
    bm25_weight: float = 0.4
    enable_reranking: bool = True
    max_initial_results: int = 20
    max_final_results: int = 5
    
    # Generation settings
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"
    generation_timeout: float = 10.0
    
    # Caching settings
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    redis_url: Optional[str] = None
    
    # Feedback settings
    enable_feedback: bool = True
    auto_adaptation: bool = True
    adaptation_threshold: int = 10


class AdvancedRAGSystem:
    """
    Complete advanced RAG system integrating all improvements.
    Drop-in replacement for existing RAG with significantly better performance.
    """
    
    def __init__(self, 
                 config: Optional[AdvancedRAGConfig] = None,
                 chroma_collection=None,
                 collection_name: str = "docscanner_advanced"):
        """
        Initialize the advanced RAG system.
        
        Args:
            config: Configuration object
            chroma_collection: Existing ChromaDB collection
            collection_name: Collection name if creating new
        """
        self.config = config or AdvancedRAGConfig()
        self.collection_name = collection_name
        self.chroma_collection = chroma_collection
        
        # Initialize components
        self.chunker = None
        self.embedding_manager = None
        self.retriever = None
        self.prompt_manager = None
        self.feedback_system = None
        self.cache = None
        
        # Performance tracking
        self.performance_stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_response_time': 0.0,
            'successful_responses': 0,
            'failed_responses': 0,
            'user_satisfaction': 0.0
        }
        
        # Initialize all components
        self._initialize_components()
        
        logger.info(f"✅ Advanced RAG system initialized with {collection_name}")
    
    def _initialize_components(self):
        """Initialize all RAG system components."""
        try:
            # 1. Initialize chunking system
            self.chunker = AdvancedSemanticChunker(
                target_chunk_size=self.config.chunk_target_size,
                min_chunk_size=self.config.chunk_min_size,
                max_chunk_size=self.config.chunk_max_size,
                overlap_size=self.config.chunk_overlap
            )
            logger.info("✅ Advanced chunker initialized")
            
            # 2. Initialize embedding manager
            self.embedding_manager = get_embedding_manager(
                provider=self.config.embedding_provider,
                model_name=self.config.embedding_model
            )
            logger.info("✅ Advanced embedding manager initialized")
            
            # 3. Initialize retrieval system (requires ChromaDB collection)
            if self.chroma_collection:
                self.retriever = AdvancedHybridRetriever(
                    chroma_collection=self.chroma_collection,
                    semantic_weight=self.config.semantic_weight,
                    bm25_weight=self.config.bm25_weight,
                    enable_reranking=self.config.enable_reranking,
                    max_initial_results=self.config.max_initial_results,
                    max_final_results=self.config.max_final_results
                )
                logger.info("✅ Advanced retriever initialized")
            
            # 4. Initialize prompt manager
            self.prompt_manager = get_prompt_manager()
            logger.info("✅ Advanced prompt manager initialized")
            
            # 5. Initialize feedback system
            if self.config.enable_feedback:
                self.feedback_system = get_feedback_system()
                logger.info("✅ Feedback system initialized")
            
            # 6. Initialize caching
            if self.config.enable_caching:
                self._initialize_cache()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG components: {e}")
            raise
    
    def _initialize_cache(self):
        """Initialize caching system (Redis or in-memory)."""
        if REDIS_AVAILABLE and self.config.redis_url:
            try:
                self.cache = redis.from_url(self.config.redis_url)
                self.cache.ping()  # Test connection
                logger.info("✅ Redis cache initialized")
                return
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
        
        # Fallback to in-memory cache
        self.cache = {}
        logger.info("✅ In-memory cache initialized")
    
    def ingest_document_advanced(self,
                                document_text: str,
                                source_doc_id: str,
                                product: str = "docscanner",
                                version: str = "1.0",
                                additional_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Ingest a document using advanced chunking and embedding.
        
        Args:
            document_text: Raw document text
            source_doc_id: Unique document identifier
            product: Product name
            version: Version string
            additional_metadata: Extra metadata
            
        Returns:
            Number of chunks created
        """
        logger.info(f"📥 Ingesting document: {source_doc_id}")
        
        try:
            # Step 1: Advanced semantic chunking
            chunks = self.chunker.chunk_document_advanced(
                document_text=document_text,
                source_doc_id=source_doc_id,
                product=product,
                version=version,
                additional_metadata=additional_metadata or {}
            )
            
            if not chunks:
                logger.warning(f"No chunks created for document: {source_doc_id}")
                return 0
            
            # Step 2: Generate enhanced embeddings for each chunk
            if not self.chroma_collection:
                logger.error("ChromaDB collection not available for ingestion")
                return 0
            
            chunk_texts = []
            chunk_ids = []
            chunk_metadatas = []
            
            for chunk in chunks:
                # Enhance text with metadata for better embeddings
                enhanced_text = self.embedding_manager.enhance_text_for_embedding(
                    text=chunk.text,
                    metadata=asdict(chunk)
                )
                
                chunk_texts.append(enhanced_text)
                chunk_ids.append(chunk.chunk_id)
                
                # Prepare metadata for ChromaDB
                metadata = {
                    'source_doc_id': chunk.source_doc_id,
                    'product': chunk.product,
                    'version': chunk.version,
                    'section_title': chunk.section_title,
                    'section_level': chunk.section_level,
                    'paragraph_index': chunk.paragraph_index,
                    'chunk_index': chunk.chunk_index,
                    'sentence_range': chunk.sentence_range,
                    'structural_type': chunk.structural_type,
                    'token_count': chunk.token_count,
                    'char_count': chunk.char_count,
                    'created_at': chunk.created_at,
                    'rule_tags': json.dumps(chunk.rule_tags)
                }
                chunk_metadatas.append(metadata)
            
            # Step 3: Batch generate embeddings
            embeddings = self.embedding_manager.get_embeddings_batch(chunk_texts)
            
            # Step 4: Add to ChromaDB collection
            self.chroma_collection.add(
                embeddings=embeddings,
                documents=chunk_texts,
                ids=chunk_ids,
                metadatas=chunk_metadatas
            )
            
            # Step 5: Update retriever indexes
            if self.retriever:
                self.retriever._build_indexes()
            
            logger.info(f"✅ Document ingested: {len(chunks)} chunks created for {source_doc_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest document {source_doc_id}: {e}")
            return 0
    
    def get_advanced_suggestion(self,
                               feedback_text: str,
                               sentence_context: str = "",
                               document_type: str = "general",
                               document_content: str = "",
                               rule_id: str = "unknown",
                               user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get advanced AI suggestion using the complete enhanced pipeline.
        
        Args:
            feedback_text: Description of the writing issue
            sentence_context: The problematic sentence
            document_type: Type of document
            document_content: Full document content for context
            rule_id: ID of the violated rule
            user_context: Additional user context
            
        Returns:
            Enhanced suggestion with sources, confidence, and tracking
        """
        start_time = time.time()
        self.performance_stats['total_queries'] += 1
        
        # Generate unique query ID for tracking
        query_id = hashlib.md5(f"{feedback_text}_{sentence_context}".encode()).hexdigest()[:12]
        
        try:
            # Step 1: Check cache first
            if self.config.enable_caching:
                cached_result = self._get_cached_result(query_id)
                if cached_result:
                    self.performance_stats['cache_hits'] += 1
                    logger.info(f"🎯 Cache hit for query: {query_id}")
                    return cached_result
            
            # Step 2: Advanced retrieval
            if not self.retriever:
                logger.error("Retriever not available")
                return self._generate_fallback_response(feedback_text, sentence_context)
            
            # Build enhanced query
            query_text = self._build_enhanced_query(feedback_text, sentence_context, document_type)
            
            # Apply smart filtering
            filters = self._build_smart_filters(document_content, document_type, user_context)
            
            # Retrieve with advanced hybrid search
            retrieval_results = self.retriever.retrieve_advanced(
                query=query_text,
                filters=filters,
                use_semantic=True,
                use_bm25=True,
                use_reranking=self.config.enable_reranking
            )
            
            # Step 3: Generate response with structured prompting
            if not retrieval_results:
                logger.warning(f"No retrieval results for query: {query_id}")
                return self._generate_fallback_response(feedback_text, sentence_context)
            
            # Build context for prompt
            context = {
                'product': self._extract_product(document_content),
                'document_type': document_type,
                'section': self._extract_section(sentence_context),
                'audience': user_context.get('audience', 'technical') if user_context else 'technical'
            }
            
            # Convert retrieval results to prompt format
            retrieved_chunks = [
                {
                    'text': result.text,
                    'metadata': result.metadata,
                    'score': result.hybrid_score
                }
                for result in retrieval_results
            ]
            
            # Generate structured prompt
            template_name = self._select_prompt_template(feedback_text, rule_id)
            prompt = self.prompt_manager.build_constrained_prompt(
                sentence=sentence_context,
                issue=feedback_text,
                context=context,
                retrieved_chunks=retrieved_chunks,
                template_name=template_name
            )
            
            # Step 4: Call LLM with structured prompt
            llm_response = self._call_llm(prompt)
            
            # Step 5: Parse and validate response
            parsed_response = self._parse_llm_response(llm_response, template_name)
            
            # Step 6: Build comprehensive result
            result = self._build_comprehensive_result(
                parsed_response=parsed_response,
                retrieval_results=retrieval_results,
                query_id=query_id,
                response_time=time.time() - start_time,
                method="advanced_rag"
            )
            
            # Step 7: Cache the result
            if self.config.enable_caching:
                self._cache_result(query_id, result)
            
            # Step 8: Update performance stats
            self.performance_stats['successful_responses'] += 1
            self._update_response_time(time.time() - start_time)
            
            logger.info(f"✅ Advanced suggestion generated: {query_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Advanced suggestion failed: {e}")
            self.performance_stats['failed_responses'] += 1
            return self._generate_fallback_response(feedback_text, sentence_context)
    
    def record_user_feedback(self,
                            query_id: str,
                            user_rating: int,
                            was_helpful: bool,
                            was_implemented: bool,
                            user_comment: Optional[str] = None) -> bool:
        """
        Record user feedback for continuous improvement.
        
        Args:
            query_id: Query identifier
            user_rating: Rating 1-5
            was_helpful: Whether suggestion was helpful
            was_implemented: Whether user implemented the suggestion
            user_comment: Optional comment
            
        Returns:
            True if feedback recorded successfully
        """
        if not self.feedback_system:
            logger.warning("Feedback system not available")
            return False
        
        try:
            feedback = UserFeedback(
                feedback_id=f"{query_id}_{int(time.time())}",
                query=query_id,  # This would need to be expanded with actual query text
                retrieved_chunks=[],  # Would need to be stored from original query
                generated_response="",  # Would need to be stored from original query
                user_rating=user_rating,
                user_comment=user_comment,
                was_helpful=was_helpful,
                was_implemented=was_implemented,
                timestamp=datetime.now().isoformat(),
                response_time=0.0,  # Would need to be stored from original query
                method_used="advanced_rag"
            )
            
            success = self.feedback_system.record_user_feedback(feedback)
            
            if success:
                # Update satisfaction metric
                self._update_satisfaction_metric(user_rating)
                logger.info(f"✅ User feedback recorded: {query_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to record user feedback: {e}")
            return False
    
    def _build_enhanced_query(self, feedback_text: str, sentence_context: str, document_type: str) -> str:
        """Build enhanced query for better retrieval."""
        query_parts = []
        
        # Add feedback terms
        if feedback_text:
            query_parts.append(feedback_text)
        
        # Add key terms from sentence
        if sentence_context:
            # Extract important terms (avoid common words)
            important_words = [
                word for word in sentence_context.lower().split()
                if len(word) > 3 and word not in {'this', 'that', 'with', 'from', 'they', 'were', 'been', 'have', 'will'}
            ]
            query_parts.extend(important_words[:5])
        
        # Add document type context
        if document_type != "general":
            query_parts.append(document_type)
        
        return " ".join(query_parts)
    
    def _build_smart_filters(self, 
                           document_content: str, 
                           document_type: str,
                           user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build smart metadata filters for retrieval."""
        filters = {}
        
        # Product detection
        product = self._extract_product(document_content)
        if product:
            filters['product'] = product
        
        # Rule-based filtering
        if user_context and user_context.get('preferred_rules'):
            filters['rule_tags'] = user_context['preferred_rules']
        
        return filters
    
    def _extract_product(self, document_content: str) -> Optional[str]:
        """Extract product name from document content."""
        if not document_content:
            return None
        
        content_lower = document_content.lower()
        
        # Simple product detection
        products = {
            'profinet': 'Profinet IO Connector',
            'opcua': 'OPC UA Connector', 
            'modbus': 'Modbus Connector',
            'simatic': 'SIMATIC',
            'wincc': 'WinCC'
        }
        
        for keyword, product in products.items():
            if keyword in content_lower:
                return product
        
        return None
    
    def _extract_section(self, sentence_context: str) -> str:
        """Extract section context from sentence."""
        # Simple heuristic - could be improved with more sophisticated NLP
        if "configure" in sentence_context.lower():
            return "Configuration"
        elif "install" in sentence_context.lower():
            return "Installation"
        elif "error" in sentence_context.lower():
            return "Troubleshooting"
        else:
            return "General"
    
    def _select_prompt_template(self, feedback_text: str, rule_id: str) -> str:
        """Select appropriate prompt template based on issue type."""
        feedback_lower = feedback_text.lower()
        
        if "passive voice" in feedback_lower or "active voice" in feedback_lower:
            return "style_rewrite"
        elif "technical" in feedback_lower or rule_id in ['technical_accuracy', 'terminology']:
            return "technical_accuracy"
        else:
            return "context_suggestion"
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with the structured prompt."""
        try:
            import requests
            
            response = requests.post(
                f"{self.config.ollama_url}/api/generate",
                json={
                    "model": self.config.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistency
                        "top_p": 0.9,
                        "num_predict": 200  # Limit response length
                    }
                },
                timeout=self.config.generation_timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"LLM call failed: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return ""
    
    def _parse_llm_response(self, response: str, template_name: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                parsed = json.loads(response)
                if self.prompt_manager.validate_output_format(response, template_name):
                    return parsed
            
            # Fallback parsing for non-JSON responses
            return {
                'suggestion': response.strip(),
                'explanation': 'Generated by advanced RAG system',
                'confidence': 'medium'
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                'suggestion': response.strip() if response else 'Unable to generate suggestion',
                'explanation': 'Fallback parsing used',
                'confidence': 'low'
            }
    
    def _build_comprehensive_result(self,
                                   parsed_response: Dict[str, Any],
                                   retrieval_results: List[AdvancedRetrievalResult],
                                   query_id: str,
                                   response_time: float,
                                   method: str) -> Dict[str, Any]:
        """Build comprehensive result with all metadata."""
        # Extract main suggestion
        suggestion = (
            parsed_response.get('rewrite') or 
            parsed_response.get('suggestion') or 
            'Review and improve the text'
        )
        
        # Extract explanation
        explanation = (
            parsed_response.get('explanation') or
            parsed_response.get('reasoning') or
            'Generated using advanced RAG system'
        )
        
        # Calculate confidence
        confidence = self._calculate_overall_confidence(parsed_response, retrieval_results)
        
        # Format sources
        sources = self._format_sources(retrieval_results)
        
        return {
            'suggestion': suggestion,
            'ai_answer': explanation,
            'confidence': confidence,
            'method': method,
            'sources': sources,
            'query_id': query_id,
            'response_time': response_time,
            'retrieval_quality': {
                'num_results': len(retrieval_results),
                'avg_score': sum(r.hybrid_score for r in retrieval_results) / max(1, len(retrieval_results)),
                'reranked': any(r.rerank_score > 0 for r in retrieval_results)
            },
            'context_used': {
                'embedding_provider': self.embedding_manager.provider,
                'retrieval_method': 'hybrid_with_reranking' if self.config.enable_reranking else 'hybrid',
                'prompt_template': 'advanced_structured'
            }
        }
    
    def _calculate_overall_confidence(self, 
                                    parsed_response: Dict[str, Any],
                                    retrieval_results: List[AdvancedRetrievalResult]) -> str:
        """Calculate overall confidence score."""
        factors = []
        
        # LLM confidence
        llm_confidence = parsed_response.get('confidence', 'medium')
        if llm_confidence == 'high':
            factors.append(0.8)
        elif llm_confidence == 'medium':
            factors.append(0.6)
        else:
            factors.append(0.4)
        
        # Retrieval quality
        if retrieval_results:
            avg_score = sum(r.hybrid_score for r in retrieval_results) / len(retrieval_results)
            factors.append(min(1.0, avg_score))
        
        # Overall calculation
        overall_score = sum(factors) / len(factors) if factors else 0.5
        
        if overall_score > 0.75:
            return 'high'
        elif overall_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _format_sources(self, retrieval_results: List[AdvancedRetrievalResult]) -> List[Dict[str, Any]]:
        """Format sources for UI display."""
        sources = []
        
        for result in retrieval_results[:3]:  # Top 3 sources
            source = {
                'text': result.text[:200] + "..." if len(result.text) > 200 else result.text,
                'source_doc': result.metadata.get('source_doc_id', 'Unknown'),
                'section': result.metadata.get('section_title', 'Unknown'),
                'confidence': result.hybrid_score,
                'relevance': result.relevance_explanation
            }
            sources.append(source)
        
        return sources
    
    def _generate_fallback_response(self, feedback_text: str, sentence_context: str) -> Dict[str, Any]:
        """Generate fallback response when advanced system fails."""
        return {
            'suggestion': f"Review the text to address: {feedback_text}",
            'ai_answer': 'Basic fallback - advanced system unavailable',
            'confidence': 'low',
            'method': 'fallback',
            'sources': [],
            'note': 'Advanced RAG system unavailable'
        }
    
    def _get_cached_result(self, query_id: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        try:
            if isinstance(self.cache, dict):
                # In-memory cache
                return self.cache.get(query_id)
            else:
                # Redis cache
                cached = self.cache.get(query_id)
                if cached:
                    return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    def _cache_result(self, query_id: str, result: Dict[str, Any]):
        """Cache result for future use."""
        try:
            if isinstance(self.cache, dict):
                # In-memory cache with size limit
                if len(self.cache) > 1000:
                    # Remove oldest entries
                    keys_to_remove = list(self.cache.keys())[:100]
                    for key in keys_to_remove:
                        del self.cache[key]
                self.cache[query_id] = result
            else:
                # Redis cache
                self.cache.setex(
                    query_id, 
                    self.config.cache_ttl, 
                    json.dumps(result, default=str)
                )
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def _update_response_time(self, response_time: float):
        """Update average response time metric."""
        current_avg = self.performance_stats['avg_response_time']
        total_queries = self.performance_stats['total_queries']
        
        new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
        self.performance_stats['avg_response_time'] = new_avg
    
    def _update_satisfaction_metric(self, rating: int):
        """Update user satisfaction metric."""
        # Simple running average of ratings
        current_satisfaction = self.performance_stats['user_satisfaction']
        if current_satisfaction == 0:
            self.performance_stats['user_satisfaction'] = rating
        else:
            # Weighted average favoring recent feedback
            self.performance_stats['user_satisfaction'] = (current_satisfaction * 0.8) + (rating * 0.2)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and performance metrics."""
        status = {
            'system_health': 'operational',
            'components': {
                'chunker': self.chunker is not None,
                'embedding_manager': self.embedding_manager is not None,
                'retriever': self.retriever is not None,
                'prompt_manager': self.prompt_manager is not None,
                'feedback_system': self.feedback_system is not None,
                'cache': self.cache is not None
            },
            'performance': self.performance_stats.copy(),
            'configuration': {
                'embedding_provider': self.embedding_manager.provider if self.embedding_manager else None,
                'caching_enabled': self.config.enable_caching,
                'feedback_enabled': self.config.enable_feedback,
                'reranking_enabled': self.config.enable_reranking
            }
        }
        
        # Add component-specific stats
        if self.embedding_manager:
            status['embedding_stats'] = self.embedding_manager.get_embedding_stats()
        
        if self.retriever:
            status['retrieval_stats'] = self.retriever.get_retrieval_stats()
        
        if self.feedback_system:
            status['feedback_analytics'] = self.feedback_system.get_feedback_analytics(days=7)
        
        return status


def create_advanced_rag_system(chroma_collection,
                              config: Optional[AdvancedRAGConfig] = None) -> AdvancedRAGSystem:
    """
    Create a fully configured advanced RAG system.
    
    Args:
        chroma_collection: ChromaDB collection
        config: Optional configuration
        
    Returns:
        Configured advanced RAG system
    """
    return AdvancedRAGSystem(
        config=config or AdvancedRAGConfig(),
        chroma_collection=chroma_collection
    )


# Global instance
_global_advanced_rag = None

def get_advanced_rag_system(chroma_collection=None,
                           config: Optional[AdvancedRAGConfig] = None) -> AdvancedRAGSystem:
    """
    Get global advanced RAG system instance.
    
    Args:
        chroma_collection: ChromaDB collection
        config: Optional configuration
        
    Returns:
        Global advanced RAG system
    """
    global _global_advanced_rag
    
    if _global_advanced_rag is None and chroma_collection:
        _global_advanced_rag = create_advanced_rag_system(chroma_collection, config)
    
    return _global_advanced_rag
