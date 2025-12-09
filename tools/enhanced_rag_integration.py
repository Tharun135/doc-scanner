# enhanced_rag_integration.py
"""
Practical integration of Enhanced RAG with existing DocScanner system.
This file provides drop-in replacements and integration helpers.
"""
import logging
import os
import sys
from typing import Dict, Any, Optional, List

# Add enhanced_rag to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'enhanced_rag'))

try:
    from enhanced_rag import (
        get_enhanced_rag_system,
        get_enhanced_store,
        quick_setup
    )
    ENHANCED_RAG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced RAG not available: {e}")
    ENHANCED_RAG_AVAILABLE = False

logger = logging.getLogger(__name__)

def _fix_title_case_issues(text: str) -> str:
    """
    Fix inappropriate title case formatting that might come from AI responses.
    Ensures proper sentence case instead of Title Case for normal sentences.
    """
    if not text or len(text.strip()) == 0:
        return text
        
    # Split into words
    words = text.split()
    
    # Check if this looks like inappropriate title case
    # (more than 60% of words are title cased, excluding proper nouns)
    title_case_count = 0
    total_checkable_words = 0
    
    for i, word in enumerate(words):
        # Skip first word (should be capitalized), articles, prepositions, etc.
        if i == 0 or len(word) <= 2:
            continue
        if word.lower() in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were']:
            continue
            
        total_checkable_words += 1
        if word and len(word) > 1 and word[0].isupper() and word[1:].islower():
            title_case_count += 1
    
    # If more than 60% of content words are title cased, fix it
    if total_checkable_words > 2 and title_case_count / total_checkable_words > 0.6:
        fixed_words = []
        for i, word in enumerate(words):
            if i == 0:
                # Keep first word capitalized
                fixed_words.append(word)
            elif word.lower() in ['api', 'gui', 'db', 'sql', 'html', 'css', 'json', 'xml', 'url', 'ui', 'ux']:
                # Keep technical acronyms uppercase
                fixed_words.append(word.upper())
            elif word.isupper() and len(word) <= 4:
                # Keep short acronyms uppercase  
                fixed_words.append(word)
            else:
                # Convert to lowercase except for proper nouns
                fixed_words.append(word.lower())
        
        return ' '.join(fixed_words)
    
    return text

class EnhancedRAGIntegration:
    """
    Integration layer for Enhanced RAG with existing DocScanner system.
    Provides backwards compatibility and gradual migration path.
    """
    
    def __init__(self, enable_fallback: bool = True):
        """
        Initialize enhanced RAG integration.
        
        Args:
            enable_fallback: Whether to fall back to original system if enhanced fails
        """
        self.enable_fallback = enable_fallback
        self.enhanced_system = None
        self.original_system = None
        self.stats = {
            "enhanced_calls": 0,
            "fallback_calls": 0,
            "total_calls": 0
        }
        
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize both enhanced and original systems"""
        # Try to initialize enhanced system
        if ENHANCED_RAG_AVAILABLE:
            try:
                self.enhanced_system = get_enhanced_rag_system()
                logger.info("✅ Enhanced RAG system initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced RAG initialization failed: {e}")
                self.enhanced_system = None
        
        # Initialize original system as fallback
        if self.enable_fallback:
            try:
                # Import original RAG system
                from scripts.ollama_rag_system import OllamaRAGSystem
                self.original_system = OllamaRAGSystem()
                logger.info("✅ Original RAG system available as fallback")
            except Exception as e:
                logger.warning(f"⚠️ Original RAG system not available: {e}")
                self.original_system = None
    
    def get_rag_suggestion(self,
                          feedback_text: str,
                          sentence_context: str = "",
                          document_type: str = "general",
                          document_content: str = "",
                          rule_id: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Enhanced RAG suggestion with automatic fallback.
        Drop-in replacement for existing get_rag_suggestion calls.
        
        Args:
            feedback_text: Description of the writing issue
            sentence_context: The problematic sentence
            document_type: Type of document
            document_content: Full document content
            rule_id: ID of the rule that was violated
        
        Returns:
            Suggestion response or None
        """
        self.stats["total_calls"] += 1
        
        # Try enhanced system first
        if self.enhanced_system:
            try:
                response = self.enhanced_system.get_rag_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context,
                    document_type=document_type,
                    document_content=document_content,
                    rule_id=rule_id
                )
                
                if response:
                    self.stats["enhanced_calls"] += 1
                    return self._convert_enhanced_response(response)
                    
            except Exception as e:
                logger.warning(f"Enhanced RAG failed: {e}")
        
        # Fall back to original system
        if self.enable_fallback and self.original_system:
            try:
                response = self.original_system.get_rag_suggestion(
                    feedback_text=feedback_text,
                    sentence_context=sentence_context,
                    document_type=document_type,
                    document_content=document_content
                )
                
                if response:
                    self.stats["fallback_calls"] += 1
                    return response
                    
            except Exception as e:
                logger.warning(f"Original RAG also failed: {e}")
        
        return None
    
    def _convert_enhanced_response(self, enhanced_response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert enhanced response format to original format for compatibility"""
        return {
            "suggestion": enhanced_response.get("suggested_correction", ""),
            "confidence": enhanced_response.get("confidence", "medium"),
            "method": enhanced_response.get("method", "enhanced_rag"),
            "sources": enhanced_response.get("sources", []),
            "explanation": enhanced_response.get("explanation", ""),
            "original_sentence": enhanced_response.get("original_sentence", ""),
            # Keep enhanced fields for future use
            "enhanced_response": enhanced_response
        }
    
    def ingest_document(self,
                       document_text: str,
                       source_doc_id: str,
                       product: str = "docscanner",
                       version: str = "1.0") -> int:
        """
        Ingest document with enhanced chunking.
        
        Returns:
            Number of chunks created
        """
        if self.enhanced_system:
            try:
                return self.enhanced_system.vector_store.ingest_document(
                    document_text=document_text,
                    source_doc_id=source_doc_id,
                    product=product,
                    version=version
                )
            except Exception as e:
                logger.error(f"Enhanced document ingestion failed: {e}")
        
        return 0
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = self.stats.copy()
        
        if self.enhanced_system:
            try:
                enhanced_metrics = self.enhanced_system.get_system_metrics()
                stats["enhanced_metrics"] = enhanced_metrics
            except Exception as e:
                stats["enhanced_metrics_error"] = str(e)
        
        # Calculate usage percentages
        if stats["total_calls"] > 0:
            stats["enhanced_usage_rate"] = stats["enhanced_calls"] / stats["total_calls"]
            stats["fallback_usage_rate"] = stats["fallback_calls"] / stats["total_calls"]
        
        return stats
    
    def migrate_existing_data(self) -> bool:
        """Migrate existing ChromaDB data to enhanced format"""
        if not self.enhanced_system:
            logger.error("Enhanced system not available for migration")
            return False
        
        try:
            success = self.enhanced_system.vector_store.migrate_from_existing_collection()
            if success:
                logger.info("✅ Successfully migrated existing data")
            return success
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False


# Global instance for easy integration
_enhanced_rag_integration = None

def get_enhanced_rag_integration() -> EnhancedRAGIntegration:
    """Get global enhanced RAG integration instance"""
    global _enhanced_rag_integration
    if _enhanced_rag_integration is None:
        _enhanced_rag_integration = EnhancedRAGIntegration()
    return _enhanced_rag_integration


# Drop-in replacement functions for existing code
def enhanced_enrich_issue_with_solution(issue: dict) -> dict:
    """
    Enhanced version of enrich_issue_with_solution with proper RAG integration.
    Uses ChromaDB for retrieval and Ollama for generation with robust fallbacks.
    """
    import chromadb
    import requests
    import time
    
    feedback_text = issue.get("message", "")
    sentence_context = issue.get("context", "")
    rule_id = issue.get("issue_type", "unknown")
    
    logger.info(f"[ENHANCED RAG] Processing: {feedback_text[:50]}... | Context: {sentence_context[:50]}...")
    
    # Step 1: Try ChromaDB + Ollama RAG (the real RAG system)
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = client.list_collections()
        
        if collections:
            # Use the first available collection (preferably docscanner_rules)
            collection_name = None
            for col in collections:
                if 'rules' in col.name.lower() or 'enhanced' in col.name.lower():
                    collection_name = col.name
                    break
            
            if not collection_name and collections:
                collection_name = collections[0].name
                
            if collection_name:
                collection = client.get_collection(collection_name)
                
                # Query ChromaDB for relevant writing rules
                query_text = f"{feedback_text} {sentence_context} {rule_id}"
                results = collection.query(
                    query_texts=[query_text],
                    n_results=3
                )
                
                if results and results.get('documents') and results['documents'][0]:
                    # Got relevant documents from ChromaDB
                    documents = results['documents'][0]
                    metadatas = results.get('metadatas', [[]])[0]
                    distances = results.get('distances', [[]])[0]
                    
                    logger.info(f"[ENHANCED RAG] Found {len(documents)} relevant documents in ChromaDB")
                    
                    # Create RAG context from retrieved documents
                    rag_context = ""
                    sources = []
                    
                    for i, (doc, meta, dist) in enumerate(zip(documents[:2], metadatas[:2], distances[:2])):
                        rule_name = meta.get('rule_id', f'rule_{i+1}')
                        rag_context += f"Rule {i+1} ({rule_name}):\n{doc[:300]}\n\n"
                        sources.append({
                            "rule_id": rule_name,
                            "similarity": round(1.0 - float(dist), 3),
                            "preview": doc[:100]
                        })
                    
                    # Try Ollama with retrieved context
                    try:
                        # Create enhanced prompt with RAG context
                        if "passive voice" in feedback_text.lower():
                            enhanced_prompt = f"""Based on these writing rules:

{rag_context}

Convert this passive voice sentence to active voice:
PASSIVE: "{sentence_context}"

Provide the active voice version:
ACTIVE: """
                        elif "long sentence" in feedback_text.lower() or "break" in feedback_text.lower():
                            enhanced_prompt = f"""Based on these writing rules:

{rag_context}

Break this long sentence into two shorter sentences:
ORIGINAL: "{sentence_context}"

Sentence 1:
Sentence 2:"""
                        elif "sentence case" in feedback_text.lower() or "capital" in feedback_text.lower():
                            enhanced_prompt = f"""Based on these writing rules:

{rag_context}

Fix the capitalization in this sentence:
ORIGINAL: "{sentence_context}"
CORRECTED: """
                        else:
                            enhanced_prompt = f"""Based on these writing rules:

{rag_context}

Fix this writing issue: {feedback_text}
ORIGINAL: "{sentence_context}"
IMPROVED: """
                        
                        # Call Ollama with proper timeout
                        response = requests.post('http://localhost:11434/api/generate', json={
                            'model': 'phi3:mini',  # Use phi3:mini as it's reliable
                            'prompt': enhanced_prompt,
                            'stream': False,
                            'options': {
                                'temperature': 0.1,
                                'top_p': 0.8,
                                'num_predict': 100,
                                'num_ctx': 1500
                            }
                        }, timeout=8)  # 8 second timeout
                        
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result.get('response', '').strip()
                            
                            if ai_response and len(ai_response) > 10:
                                logger.info(f"[ENHANCED RAG] ✅ Ollama + ChromaDB success: {ai_response[:50]}...")
                                
                                # Extract the correction from AI response
                                proposed_rewrite = sentence_context  # Default fallback
                                
                                # Extract based on prompt format
                                if "ACTIVE:" in ai_response:
                                    active_part = ai_response.split("ACTIVE:")[-1].strip()
                                    if active_part and len(active_part) > 5:
                                        proposed_rewrite = active_part.replace('"', '').strip()
                                elif "CORRECTED:" in ai_response:
                                    corrected_part = ai_response.split("CORRECTED:")[-1].strip()
                                    if corrected_part and len(corrected_part) > 5:
                                        proposed_rewrite = corrected_part.replace('"', '').strip()
                                elif "IMPROVED:" in ai_response:
                                    improved_part = ai_response.split("IMPROVED:")[-1].strip()
                                    if improved_part and len(improved_part) > 5:
                                        proposed_rewrite = improved_part.replace('"', '').strip()
                                elif "Sentence 1:" in ai_response and "Sentence 2:" in ai_response:
                                    # Handle sentence breaking
                                    lines = ai_response.split('\n')
                                    sent1, sent2 = "", ""
                                    for line in lines:
                                        if line.strip().startswith('Sentence 1:'):
                                            sent1 = line.split('Sentence 1:')[-1].strip().replace('"', '')
                                        elif line.strip().startswith('Sentence 2:'):
                                            sent2 = line.split('Sentence 2:')[-1].strip().replace('"', '')
                                    
                                    if sent1 and sent2:
                                        proposed_rewrite = f"{sent1}. {sent2}"
                                
                                # Apply simple deterministic fixes if AI didn't provide good correction
                                if proposed_rewrite == sentence_context or not proposed_rewrite.strip():
                                    # Use our enhanced rule-specific corrections
                                    from enhanced_rag.rule_specific_corrections import get_rule_specific_correction
                                    
                                    # Determine rule type from feedback
                                    rule_type = "general"
                                    if "passive voice" in feedback_text.lower():
                                        rule_type = "passive-voice"
                                    elif "capital" in feedback_text.lower():
                                        rule_type = "capitalization"
                                    elif "long sentence" in feedback_text.lower():
                                        rule_type = "long-sentence"
                                    
                                    corrected = get_rule_specific_correction(sentence_context, rule_type, feedback_text)
                                    if corrected != sentence_context:
                                        proposed_rewrite = corrected
                                    else:
                                        # Legacy fallbacks for specific cases
                                        if "sentence case" in feedback_text.lower() or "capital" in feedback_text.lower():
                                            proposed_rewrite = sentence_context[0].upper() + sentence_context[1:] if len(sentence_context) > 1 else sentence_context.upper()
                                        else:
                                            proposed_rewrite = sentence_context  # Don't add "Improved:" prefix
                                
                                # Return enhanced RAG response with title case protection
                                proposed_rewrite = _fix_title_case_issues(proposed_rewrite)
                                issue["solution_text"] = ai_response
                                issue["proposed_rewrite"] = proposed_rewrite
                                issue["sources"] = sources
                                issue["method"] = "enhanced_rag_chromadb_ollama"
                                issue["confidence"] = "high"
                                
                                return issue
                        
                        else:
                            logger.warning(f"[ENHANCED RAG] Ollama error {response.status_code}")
                            
                    except requests.exceptions.Timeout:
                        logger.warning("[ENHANCED RAG] Ollama timeout - using ChromaDB only")
                    except requests.exceptions.ConnectionError:
                        logger.warning("[ENHANCED RAG] Ollama connection error - using ChromaDB only")
                    except Exception as e:
                        logger.warning(f"[ENHANCED RAG] Ollama error: {e}")
                    
                    # ChromaDB-only fallback (still better than basic fallback)
                    if documents and metadatas:
                        best_doc = documents[0]
                        best_meta = metadatas[0] if metadatas else {}
                        
                        # Extract solution from metadata if available
                        solution = best_meta.get('solution', best_meta.get('explanation', ''))
                        if not solution:
                            solution = f"Based on the retrieved writing rule: {best_doc[:200]}..."
                        
                        # Apply deterministic correction based on rule type
                        proposed_rewrite = sentence_context
                        
                        # Use enhanced rule-specific corrections
                        from enhanced_rag.rule_specific_corrections import get_rule_specific_correction
                        
                        # Determine rule type from feedback
                        rule_type = "general"
                        if "passive voice" in feedback_text.lower():
                            rule_type = "passive-voice"
                        elif "capital" in feedback_text.lower():
                            rule_type = "capitalization"
                        elif "long sentence" in feedback_text.lower():
                            rule_type = "long-sentence"
                        
                        corrected = get_rule_specific_correction(sentence_context, rule_type, feedback_text)
                        if corrected != sentence_context:
                            proposed_rewrite = corrected
                        else:
                            # Legacy fallbacks
                            if "sentence case" in feedback_text.lower() or "capital letter" in feedback_text.lower():
                                proposed_rewrite = sentence_context[0].upper() + sentence_context[1:] if len(sentence_context) > 1 else sentence_context.upper()
                            elif "long sentence" in feedback_text.lower() and len(sentence_context) > 80:
                                # Simple sentence breaking
                                mid_point = len(sentence_context) // 2
                                split_point = sentence_context.find(' ', mid_point)
                                if split_point > 0:
                                    proposed_rewrite = sentence_context[:split_point] + ". " + sentence_context[split_point+1:].capitalize()
                        
                        logger.info(f"[ENHANCED RAG] ✅ ChromaDB-only success with deterministic correction")
                        
                        proposed_rewrite = _fix_title_case_issues(proposed_rewrite)
                        issue["solution_text"] = solution
                        issue["proposed_rewrite"] = proposed_rewrite
                        issue["sources"] = sources
                        issue["method"] = "enhanced_rag_chromadb_only"
                        issue["confidence"] = "medium"
                        
                        return issue
                
                else:
                    logger.info("[ENHANCED RAG] No relevant documents found in ChromaDB")
            
            else:
                logger.warning("[ENHANCED RAG] No suitable ChromaDB collection found")
        
        else:
            logger.warning("[ENHANCED RAG] No ChromaDB collections found")
    
    except Exception as e:
        logger.error(f"[ENHANCED RAG] ChromaDB error: {e}")
    
    # Step 2: Enhanced fallback (still better than original system)
    logger.info("[ENHANCED RAG] Using enhanced fallback with comprehensive corrections")
    
    # Apply comprehensive rule engine for better fallback
    try:
        from enhanced_rag.comprehensive_rule_engine import get_comprehensive_correction
        
        result = get_comprehensive_correction(
            text=sentence_context,
            rule_id=rule_id,
            document_content=feedback_text,
            document_type="general"
        )
        
        if result.get('corrected') and result['corrected'] != sentence_context:
            issue["solution_text"] = result.get('explanation', f"Applied {rule_id} correction")
            issue["proposed_rewrite"] = result['corrected']
            issue["sources"] = []
            issue["method"] = "enhanced_comprehensive_fallback"
            issue["confidence"] = "medium"
            
            logger.info(f"[ENHANCED RAG] ✅ Comprehensive fallback success")
            return issue
    
    except Exception as e:
        logger.warning(f"[ENHANCED RAG] Comprehensive fallback error: {e}")
    
    # Step 3: Simple deterministic fallback using enhanced rule-specific corrections
    from enhanced_rag.rule_specific_corrections import get_rule_specific_correction
    
    # Determine rule type from feedback
    rule_type = "general"
    if "passive voice" in feedback_text.lower():
        rule_type = "passive-voice"
    elif "capital" in feedback_text.lower():
        rule_type = "capitalization"
    elif "long sentence" in feedback_text.lower():
        rule_type = "long-sentence"
    
    proposed_rewrite = get_rule_specific_correction(sentence_context, rule_type, feedback_text)
    
    # If rule-specific correction didn't help, try legacy fallbacks
    if proposed_rewrite == sentence_context:
        if "sentence case" in feedback_text.lower() or "capital letter" in feedback_text.lower():
            # Fix capitalization
            proposed_rewrite = sentence_context[0].upper() + sentence_context[1:] if len(sentence_context) > 1 else sentence_context.upper()
        elif "long sentence" in feedback_text.lower() and len(sentence_context) > 80:
            # Simple sentence breaking at conjunction
            if " and " in sentence_context:
                parts = sentence_context.split(" and ", 1)
                proposed_rewrite = f"{parts[0]}. Additionally, {parts[1]}"
            elif ", " in sentence_context and len(sentence_context.split(", ")) >= 3:
                parts = sentence_context.split(", ")
                mid = len(parts) // 2
                part1 = ", ".join(parts[:mid])
                part2 = ", ".join(parts[mid:])
                proposed_rewrite = f"{part1}. {part2.capitalize()}"
        else:
            proposed_rewrite = sentence_context  # Don't add "Improved:" prefix
    
    issue["solution_text"] = f"Applied enhanced rule-based correction for: {feedback_text}"
    proposed_rewrite = _fix_title_case_issues(proposed_rewrite)
    issue["proposed_rewrite"] = proposed_rewrite
    issue["sources"] = []
    issue["method"] = "enhanced_fallback"
    issue["confidence"] = "low"
    
    logger.info(f"[ENHANCED RAG] ✅ Deterministic fallback applied")
    return issue


def bulk_ingest_documents(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bulk ingest documents with enhanced chunking.
    
    Args:
        documents: List of dicts with 'content', 'id', 'product', 'version' keys
    
    Returns:
        Ingestion statistics
    """
    rag_integration = get_enhanced_rag_integration()
    
    stats = {
        "total_documents": len(documents),
        "successful_ingestions": 0,
        "total_chunks": 0,
        "errors": []
    }
    
    for doc in documents:
        try:
            chunk_count = rag_integration.ingest_document(
                document_text=doc.get("content", ""),
                source_doc_id=doc.get("id", "unknown"),
                product=doc.get("product", "docscanner"),
                version=doc.get("version", "1.0")
            )
            
            if chunk_count > 0:
                stats["successful_ingestions"] += 1
                stats["total_chunks"] += chunk_count
                
        except Exception as e:
            stats["errors"].append(f"Failed to ingest {doc.get('id', 'unknown')}: {e}")
    
    return stats


def setup_enhanced_rag_for_docscanner() -> bool:
    """
    One-time setup function for enhanced RAG in DocScanner.
    Call this once to migrate and configure the enhanced system.
    """
    print("🚀 Setting up Enhanced RAG for DocScanner")
    print("=" * 50)
    
    try:
        # Initialize integration
        rag_integration = get_enhanced_rag_integration()
        
        if not rag_integration.enhanced_system:
            print("❌ Enhanced RAG system not available")
            return False
        
        # Migrate existing data
        print("📦 Migrating existing data...")
        migration_success = rag_integration.migrate_existing_data()
        
        if migration_success:
            print("✅ Data migration successful")
        else:
            print("⚠️ Data migration failed, starting fresh")
        
        # Test the system
        print("🧪 Testing enhanced system...")
        test_response = rag_integration.get_rag_suggestion(
            feedback_text="passive voice detected",
            sentence_context="The file was created by the system.",
            rule_id="passive-voice"
        )
        
        if test_response:
            print("✅ Enhanced RAG system working correctly")
            print(f"  Sample correction: {test_response.get('suggestion', 'N/A')}")
            print(f"  Confidence: {test_response.get('confidence', 'N/A')}")
            print(f"  Method: {test_response.get('method', 'N/A')}")
        else:
            print("⚠️ Enhanced RAG test failed")
            return False
        
        # Show statistics
        stats = rag_integration.get_system_stats()
        if "enhanced_metrics" in stats:
            vector_stats = stats["enhanced_metrics"].get("vector_store_stats", {})
            print(f"\n📊 System ready:")
            print(f"  Total chunks: {vector_stats.get('total_chunks', 0)}")
            print(f"  Unique products: {vector_stats.get('unique_products', 0)}")
            print(f"  Hybrid retrieval: {'✅' if vector_stats.get('hybrid_retrieval_available') else '❌'}")
        
        print("\n🎉 Enhanced RAG setup complete!")
        print("\nNext steps:")
        print("1. Replace enrichment calls with enhanced_enrich_issue_with_solution()")
        print("2. Use bulk_ingest_documents() for new content")
        print("3. Monitor performance with get_enhanced_rag_integration().get_system_stats()")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


# Performance monitoring utility
def monitor_enhanced_rag_performance():
    """Monitor and report enhanced RAG performance"""
    rag_integration = get_enhanced_rag_integration()
    stats = rag_integration.get_system_stats()
    
    print("📊 Enhanced RAG Performance Report")
    print("=" * 40)
    print(f"Total calls: {stats['total_calls']}")
    print(f"Enhanced usage: {stats.get('enhanced_usage_rate', 0):.1%}")
    print(f"Fallback usage: {stats.get('fallback_usage_rate', 0):.1%}")
    
    if "enhanced_metrics" in stats:
        perf = stats["enhanced_metrics"].get("performance_metrics", {})
        print(f"Success rate: {perf.get('successful_responses', 0)} / {perf.get('total_queries', 0)}")
        print(f"Avg response time: {perf.get('avg_response_time', 0):.3f}s")
        print(f"Cache hits: {perf.get('cache_hits', 0)}")
    
    return stats


if __name__ == "__main__":
    # Run setup if called directly
    success = setup_enhanced_rag_for_docscanner()
    
    if success:
        print("\n✅ Ready to use enhanced RAG!")
        
        # Show quick usage example
        print("\n📝 Quick usage example:")
        print("""
# In your existing code, replace:
# response = existing_rag.get_rag_suggestion(...)

# With:
from enhanced_rag_integration import enhanced_enrich_issue_with_solution

issue = {
    "message": "passive voice detected",
    "context": "The file was created by the system.",
    "issue_type": "passive-voice"
}

enhanced_issue = enhanced_enrich_issue_with_solution(issue)
print(enhanced_issue["proposed_rewrite"])
""")
    else:
        print("\n❌ Setup failed - check dependencies and configuration")
