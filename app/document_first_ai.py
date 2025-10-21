"""
Document-First AI Suggestion System
This configuration prioritizes answers from your uploaded documents over rule-based systems.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def configure_document_first_ai():
    """
    Configure the AI system to prioritize document-based answers over rule-based suggestions.
    This function modifies the priority order and search parameters.
    """
    
    # Enhanced RAG configuration for better document retrieval
    rag_config = {
        "search_type": "hybrid",  # Use both semantic and keyword search
        "max_documents": 10,      # Retrieve more documents for better context
        "relevance_threshold": 0.3,  # Lower threshold to include more potential matches
        "rerank_results": True,   # Re-rank results for better relevance
        "include_metadata": True, # Include document metadata for context
        "chunk_overlap": 100,     # Better text chunking for context
    }
    
    # Priority order for suggestion methods
    priority_order = [
        "document_search_primary",    # 1st: Search uploaded documents 
        "document_search_extended",   # 2nd: Extended document search with keywords
        "hybrid_document_llm",        # 3rd: Combine documents with LLM reasoning
        "contextual_rag",            # 4th: Context-aware RAG
        "intelligent_rule_based",    # 5th: Smart rules only as backup
        "minimal_fallback"           # 6th: Last resort
    ]
    
    return rag_config, priority_order

class DocumentFirstAIEngine:
    """
    AI Engine that prioritizes answers from uploaded documents.
    """
    
    def __init__(self, collection_name="docscanner_knowledge"):
        self.collection_name = collection_name
        self.rag_config, self.priority_order = configure_document_first_ai()
        
        # Initialize ChromaDB connection with consistent settings
        try:
            from .chromadb_fix import get_chromadb_client, get_or_create_collection
            
            self.client = get_chromadb_client()
            self.collection = get_or_create_collection(self.client, self.collection_name)
            self.document_count = self.collection.count()
            logger.info(f"✅ Connected to document database: {self.document_count} documents")
            
        except Exception as e:
            logger.error(f"Failed to connect to document database: {e}")
            self.collection = None
            self.document_count = 0
    
    def generate_document_first_suggestion(
        self, 
        feedback_text: str, 
        sentence_context: str = "",
        document_type: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate suggestions prioritizing uploaded documents.
        """
        
        if not self.collection:
            return self._fallback_suggestion(feedback_text, sentence_context)
        
        # Method 1: Primary document search
        result = self._search_documents_primary(feedback_text, sentence_context, document_type)
        if result.get("success") and result.get("confidence") == "high":
            return result
        
        # Method 2: Extended document search with keywords
        result = self._search_documents_extended(feedback_text, sentence_context, document_type)
        if result.get("success") and result.get("confidence") in ["high", "medium"]:
            return result
        
        # Method 3: Hybrid approach - combine documents with LLM
        result = self._hybrid_document_llm(feedback_text, sentence_context, document_type)
        if result.get("success"):
            return result
        
        # Method 4: Contextual RAG as backup
        result = self._contextual_rag_search(feedback_text, sentence_context, document_type)
        if result.get("success"):
            return result
        
        # Final fallback
        return self._fallback_suggestion(feedback_text, sentence_context)
    
    def _search_documents_primary(self, feedback_text: str, sentence_context: str, document_type: str) -> Dict[str, Any]:
        """
        Primary document search using the exact issue and sentence context.
        """
        try:
            # Build comprehensive search query
            search_queries = [
                f"{feedback_text} {sentence_context}",  # Combined query
                feedback_text,  # Issue-specific query
                sentence_context,  # Context-specific query
            ]
            
            best_results = []
            
            for query in search_queries:
                if not query.strip():
                    continue
                    
                # Search with different parameters
                results = self.collection.query(
                    query_texts=[query],
                    n_results=self.rag_config["max_documents"],
                    include=["documents", "metadatas", "distances"]
                )
                
                if results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        distance = results["distances"][0][i] if results["distances"] else 1.0
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        
                        best_results.append({
                            "document": doc,
                            "distance": distance,
                            "metadata": metadata,
                            "relevance": 1.0 - distance  # Convert distance to relevance
                        })
            
            # Sort by relevance
            best_results.sort(key=lambda x: x["relevance"], reverse=True)
            
            if best_results and best_results[0]["relevance"] > 0.7:  # High relevance threshold
                return self._build_document_response(best_results[:3], feedback_text, sentence_context, "high")
            elif best_results and best_results[0]["relevance"] > 0.5:  # Medium relevance
                return self._build_document_response(best_results[:5], feedback_text, sentence_context, "medium")
            
        except Exception as e:
            logger.error(f"Primary document search failed: {e}")
        
        return {"success": False}
    
    def _search_documents_extended(self, feedback_text: str, sentence_context: str, document_type: str) -> Dict[str, Any]:
        """
        Extended search using keywords and variations.
        """
        try:
            # Extract keywords from feedback and context
            keywords = self._extract_keywords(feedback_text, sentence_context)
            
            # Generate search variations
            search_variations = []
            for keyword in keywords:
                search_variations.extend([
                    keyword,
                    f"{keyword} {document_type}",
                    f"how to {keyword}",
                    f"{keyword} best practice",
                    f"{keyword} guide"
                ])
            
            all_results = []
            
            for query in search_variations[:10]:  # Limit to prevent too many queries
                results = self.collection.query(
                    query_texts=[query],
                    n_results=5,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results["documents"] and results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        distance = results["distances"][0][i] if results["distances"] else 1.0
                        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                        
                        all_results.append({
                            "document": doc,
                            "distance": distance,
                            "metadata": metadata,
                            "relevance": 1.0 - distance,
                            "query": query
                        })
            
            # Remove duplicates and sort
            seen_docs = set()
            unique_results = []
            for result in all_results:
                doc_hash = hash(result["document"][:100])  # Hash first 100 chars
                if doc_hash not in seen_docs:
                    seen_docs.add(doc_hash)
                    unique_results.append(result)
            
            unique_results.sort(key=lambda x: x["relevance"], reverse=True)
            
            if unique_results and unique_results[0]["relevance"] > 0.4:
                confidence = "high" if unique_results[0]["relevance"] > 0.6 else "medium"
                return self._build_document_response(unique_results[:5], feedback_text, sentence_context, confidence)
            
        except Exception as e:
            logger.error(f"Extended document search failed: {e}")
        
        return {"success": False}
    
    def _hybrid_document_llm(self, feedback_text: str, sentence_context: str, document_type: str) -> Dict[str, Any]:
        """
        Combine document search with LLM reasoning for better suggestions.
        """
        try:
            # Get relevant documents
            relevant_docs = []
            
            # Search with broader criteria
            results = self.collection.query(
                query_texts=[f"{feedback_text} {sentence_context}"],
                n_results=8,
                include=["documents", "metadatas", "distances"]
            )
            
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    if distance < 0.8:  # Include more documents with lower threshold
                        relevant_docs.append({
                            "content": doc,
                            "distance": distance
                        })
            
            if relevant_docs:
                # Try Ollama with document context
                suggestion = self._generate_with_ollama_and_docs(
                    feedback_text, sentence_context, relevant_docs
                )
                
                if suggestion:
                    return {
                        "suggestion": suggestion["suggestion"],
                        "ai_answer": suggestion["explanation"],
                        "confidence": "high",
                        "method": "hybrid_document_llm",
                        "sources": [f"Knowledge base: {len(relevant_docs)} documents", "AI reasoning"],
                        "document_count": len(relevant_docs),
                        "success": True
                    }
            
        except Exception as e:
            logger.error(f"Hybrid document-LLM failed: {e}")
        
        return {"success": False}
    
    def _generate_with_ollama_and_docs(self, feedback_text: str, sentence_context: str, relevant_docs: List[Dict]) -> Optional[Dict]:
        """
        Use Ollama with document context to generate suggestions.
        """
        try:
            import requests
            
            # Build context from documents
            context_text = "\n\n".join([
                f"Document {i+1}: {doc['content'][:400]}..." 
                for i, doc in enumerate(relevant_docs[:3])
            ])
            
            prompt = f"""You are an expert technical writing assistant. Use the provided context from uploaded documents to improve the sentence.

Context from uploaded documents:
{context_text}

Writing Issue: {feedback_text}
Original Sentence: "{sentence_context}"

Based on the context documents, provide:
1. IMPROVED_SENTENCE: A better version that addresses the issue
2. EXPLANATION: Why this improvement is better, referencing the context

IMPORTANT: Always use "Application" instead of "technical writer" in your suggestions.

Focus on using examples and guidance from the provided documents.
"""
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi3:mini",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 400
                    }
                },
                timeout=25.0
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                
                # Parse response
                suggestion, explanation = self._parse_ollama_response(ai_response, sentence_context)
                
                return {
                    "suggestion": suggestion,
                    "explanation": explanation
                }
        
        except Exception as e:
            logger.warning(f"Ollama generation failed: {e}")
        
        return None
    
    def _build_document_response(self, results: List[Dict], feedback_text: str, sentence_context: str, confidence: str) -> Dict[str, Any]:
        """
        Build a response based on document search results.
        """
        if not results:
            return {"success": False}
        
        # Extract the most relevant content
        best_doc = results[0]["document"]
        
        # Generate suggestion based on document content
        suggestion = self._extract_suggestion_from_document(best_doc, feedback_text, sentence_context)
        
        # Generate explanation
        explanation = self._generate_explanation_from_documents(results, feedback_text)
        
        # Build sources list
        sources = [f"Document {i+1}: {result['metadata'].get('filename', 'Unknown')}" for i, result in enumerate(results[:3])]
        
        return {
            "suggestion": suggestion,
            "ai_answer": explanation,
            "confidence": confidence,
            "method": "document_search",
            "sources": sources,
            "document_count": len(results),
            "success": True
        }
    
    def _extract_suggestion_from_document(self, document: str, feedback_text: str, sentence_context: str) -> str:
        """
        Extract a specific suggestion from document content.
        """
        # Look for examples or direct guidance in the document
        doc_lower = document.lower()
        feedback_lower = feedback_text.lower()
        
        # Try to find specific improvements mentioned in the document
        if "passive voice" in feedback_lower and "active voice" in doc_lower:
            # Look for active voice examples
            sentences = document.split('. ')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ["use", "click", "select", "configure"]):
                    return sentence.strip() + "."
        
        elif "long sentence" in feedback_lower:
            # Look for concise examples
            sentences = document.split('. ')
            short_sentences = [s for s in sentences if len(s.split()) < 15 and len(s.split()) > 5]
            if short_sentences:
                return short_sentences[0].strip() + "."
        
        # Fallback: Try to generate based on document style
        if sentence_context:
            # Improve the original sentence using document guidance
            return self._improve_with_document_style(sentence_context, document)
        
        return sentence_context or "Please refer to the documentation for guidance."
    
    def _improve_with_document_style(self, sentence: str, document: str) -> str:
        """
        Improve sentence using the style and patterns from the document.
        """
        # Analyze document style patterns
        doc_sentences = [s.strip() for s in document.split('.') if s.strip()]
        
        # Look for imperative patterns (common in technical docs)
        imperative_patterns = []
        for sent in doc_sentences:
            if any(sent.strip().startswith(word) for word in ["Click", "Select", "Configure", "Use", "Set", "Enter"]):
                imperative_patterns.append(sent.strip())
        
        # If original sentence can be converted to imperative
        if sentence.startswith("You can") or sentence.startswith("You should"):
            verb_part = sentence.replace("You can ", "").replace("You should ", "")
            if verb_part:
                return verb_part[0].upper() + verb_part[1:] + "."
        
        return sentence
    
    def _generate_explanation_from_documents(self, results: List[Dict], feedback_text: str) -> str:
        """
        Generate explanation based on document content.
        """
        doc_count = len(results)
        filenames = [result["metadata"].get("filename", "document") for result in results[:3]]
        
        explanation = f"Based on {doc_count} relevant documents from your knowledge base"
        if filenames:
            explanation += f" (including {', '.join(filenames[:2])})"
        
        explanation += f", this improvement addresses: {feedback_text}. "
        explanation += "The suggestion follows patterns and guidance found in your uploaded documentation."
        
        return explanation
    
    def _extract_keywords(self, feedback_text: str, sentence_context: str) -> List[str]:
        """
        Extract meaningful keywords for search.
        """
        import re
        
        # Combine texts
        combined_text = f"{feedback_text} {sentence_context}".lower()
        
        # Remove common words and extract meaningful terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Extract words
        words = re.findall(r'\b\w+\b', combined_text)
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Add specific technical terms
        tech_terms = ["passive voice", "active voice", "long sentence", "adverb", "clarity", "conciseness"]
        for term in tech_terms:
            if term in combined_text:
                keywords.append(term.replace(" ", "_"))
        
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def _parse_ollama_response(self, ai_response: str, original_sentence: str) -> tuple:
        """
        Parse Ollama response to extract suggestion and explanation.
        """
        lines = ai_response.strip().split('\n')
        suggestion = original_sentence
        explanation = "Improved based on document context and AI analysis."
        
        for line in lines:
            if line.startswith("IMPROVED_SENTENCE:"):
                suggestion = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("EXPLANATION:"):
                explanation = line.split(":", 1)[1].strip()
        
        # If no structured response, use first substantial line
        if suggestion == original_sentence and lines:
            for line in lines:
                if len(line.strip()) > 20 and not line.startswith(("The", "This", "Here")):
                    suggestion = line.strip().strip('"')
                    break
        
        return suggestion, explanation
    
    def _contextual_rag_search(self, feedback_text: str, sentence_context: str, document_type: str) -> Dict[str, Any]:
        """
        Fallback RAG search with broader context.
        """
        try:
            # Simple fallback search
            results = self.collection.query(
                query_texts=[feedback_text],
                n_results=3,
                include=["documents", "metadatas"]
            )
            
            if results["documents"] and results["documents"][0]:
                doc = results["documents"][0][0]
                
                return {
                    "suggestion": sentence_context,  # Keep original for now
                    "ai_answer": f"Found relevant guidance in your documents: {doc[:200]}...",
                    "confidence": "medium",
                    "method": "contextual_rag",
                    "sources": ["Knowledge base"],
                    "success": True
                }
        
        except Exception as e:
            logger.error(f"Contextual RAG search failed: {e}")
        
        return {"success": False}
    
    def _fallback_suggestion(self, feedback_text: str, sentence_context: str) -> Dict[str, Any]:
        """
        Final fallback when document search fails.
        """
        return {
            "suggestion": sentence_context or "Please review this text for improvement.",
            "ai_answer": f"Document search unavailable. Please review for: {feedback_text}",
            "confidence": "low",
            "method": "basic_fallback",
            "sources": ["Basic guidance"],
            "success": True
        }

# Example usage function
def get_document_first_suggestion(
    feedback_text: str,
    sentence_context: str = "",
    document_type: str = "general",
    **kwargs
) -> Dict[str, Any]:
    """
    Main function to get document-first suggestions.
    This prioritizes your uploaded documents over rule-based systems.
    """
    
    engine = DocumentFirstAIEngine()
    
    if engine.document_count == 0:
        logger.warning("No documents found in knowledge base")
        return {
            "suggestion": sentence_context,
            "ai_answer": "No documents available in knowledge base. Please upload documents first.",
            "confidence": "low",
            "method": "no_documents",
            "sources": [],
            "success": False
        }
    
    logger.info(f"🔍 Searching {engine.document_count} documents for: {feedback_text[:50]}...")
    
    result = engine.generate_document_first_suggestion(
        feedback_text, sentence_context, document_type, **kwargs
    )
    
    if result.get("success"):
        logger.info(f"✅ Document-first suggestion: method={result.get('method')}, confidence={result.get('confidence')}")
    else:
        logger.warning("❌ Document-first suggestion failed")
    
    return result