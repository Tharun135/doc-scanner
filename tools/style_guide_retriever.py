"""
style_guide_retriever.py

Integration module for retrieving trusted style guide content from ChromaDB.
This provides the whitelist-based retrieval functionality for the DocScanner
writing improvement system.

Usage in your main pipeline:
    from style_guide_retriever import StyleGuideRetriever
    
    retriever = StyleGuideRetriever()
    guidance = retriever.get_guidance("passive voice issues")
    if guidance:
        # Use authoritative style guides in LLM prompt
        prompt = build_authoritative_prompt(sentence, guidance)
    else:
        # Fall back to your existing smart_fallback
        prompt = smart_fallback(sentence)
"""

import chromadb
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class StyleGuideRetriever:
    """Retrieves authoritative writing guidance from curated style guides."""
    
    def __init__(self, db_path: str = "./db", collection_name: str = "style_guides"):
        """
        Initialize the style guide retriever.
        
        Args:
            db_path: Path to ChromaDB database
            collection_name: Name of the style guides collection
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self._collection = None
        
    @property
    def collection(self) -> chromadb.Collection:
        """Lazy-load ChromaDB collection."""
        if self._collection is None:
            try:
                client = chromadb.PersistentClient(path=self.db_path)
                self._collection = client.get_collection(name=self.collection_name)
                logger.info(f"Connected to style guides collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to connect to style guides collection: {e}")
                raise
        return self._collection
    
    def get_guidance(
        self, 
        query: str, 
        max_results: int = 6, 
        min_similarity: float = 0.35,
        preferred_sources: Optional[List[str]] = None,
        preferred_topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve authoritative style guidance for a query.
        
        Args:
            query: Search query (e.g., "passive voice", "UI strings")
            max_results: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
            preferred_sources: List of preferred sources ("microsoft", "google")
            preferred_topics: List of preferred topics ("voice", "ui-strings", etc.)
        
        Returns:
            List of guidance items with text, metadata, and similarity scores
        """
        try:
            # Build query filters - simplified approach for ChromaDB
            where_clauses = []
            where_clauses.append({"source_trust": {"$eq": "whitelist"}})
            where_clauses.append({"license": {"$eq": "permissive"}})
            
            # Add source filter if specified
            if preferred_sources:
                where_clauses.append({"source": {"$in": preferred_sources}})
            
            # Add topic filter if specified  
            if preferred_topics:
                where_clauses.append({"topic": {"$in": preferred_topics}})
            
            # Build final where clause
            if len(where_clauses) == 1:
                where_clause = where_clauses[0]
            else:
                where_clause = {"$and": where_clauses}
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results,
                where=where_clause
            )
            
            # Process results
            guidance_items = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert cosine distance to similarity
                
                if similarity >= min_similarity:
                    guidance_items.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                        "id": results["ids"][0][i]
                    })
            
            # Sort by similarity (highest first)
            guidance_items.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.info(f"Retrieved {len(guidance_items)} guidance items for query: '{query}'")
            return guidance_items
            
        except Exception as e:
            logger.error(f"Failed to retrieve guidance for '{query}': {e}")
            return []
    
    def get_guidance_by_topic(
        self, 
        topic: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get all guidance for a specific topic.
        
        Args:
            topic: Topic name ("voice", "ui-strings", "capitalization", etc.)
            max_results: Maximum results to return
        
        Returns:
            List of guidance items for the topic
        """
        try:
            results = self.collection.get(
                where={"$and": [
                    {"source_trust": {"$eq": "whitelist"}},
                    {"license": {"$eq": "permissive"}},
                    {"topic": {"$eq": topic}}
                ]},
                limit=max_results
            )
            
            guidance_items = []
            for i in range(len(results["ids"])):
                guidance_items.append({
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i],
                    "id": results["ids"][i]
                })
            
            logger.info(f"Retrieved {len(guidance_items)} items for topic: '{topic}'")
            return guidance_items
            
        except Exception as e:
            logger.error(f"Failed to retrieve guidance for topic '{topic}': {e}")
            return []
    
    def build_authoritative_prompt(
        self, 
        sentence: str, 
        guidance_items: List[Dict[str, Any]], 
        max_context_items: int = 4
    ) -> str:
        """
        Build an LLM prompt with authoritative style guide context.
        
        Args:
            sentence: Original sentence to improve
            guidance_items: Retrieved guidance items
            max_context_items: Maximum number of guidance items to include
        
        Returns:
            Formatted prompt with authoritative context
        """
        if not guidance_items:
            return None
        
        # Build context from top guidance items
        context_bullets = []
        for item in guidance_items[:max_context_items]:
            source = item["metadata"]["source"].title()
            title = item["metadata"].get("title", "Style Guide")
            text = item["text"][:700]  # Truncate long texts
            similarity = item.get("similarity", 0)
            
            context_bullets.append(f"**[{source} Style Guide - {title}]** (relevance: {similarity:.2f})\n{text}")
        
        context = "\n\n".join(context_bullets)
        
        prompt = f"""SYSTEM: You are a technical writing editor. Follow the authoritative guidance below from trusted style guides.

AUTHORITATIVE CONTEXT (Trusted Style Guides):
{context}

USER SENTENCE:
"{sentence}"

REQUIREMENTS:
- Keep the original meaning intact
- Apply the guidance from the authoritative sources above
- Use active voice, clear language, and concise sentences
- Do not alter product names, UI labels, code snippets, or URLs
- If the sentence is already compliant with the guidelines, return it unchanged

TASK:
Provide a single improved rewrite that follows the authoritative guidance. Then provide a brief rationale that references the specific style guide recommendations used.

Return your response in JSON format:
{{"rewrite": "improved sentence here", "rationale": "Applied [Source] guidance on [specific rule]", "sources_used": ["microsoft", "google"]}}
"""
        
        return prompt
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the style guides collection."""
        try:
            # Get sample of documents for analysis
            sample = self.collection.get(limit=100)
            
            if not sample['metadatas']:
                return {"total_documents": 0, "error": "No documents found"}
            
            # Analyze metadata
            sources = {}
            topics = {}
            versions = set()
            
            for metadata in sample['metadatas']:
                source = metadata.get('source', 'unknown')
                topic = metadata.get('topic', 'unknown')
                version = metadata.get('version', 'unknown')
                
                sources[source] = sources.get(source, 0) + 1
                topics[topic] = topics.get(topic, 0) + 1
                versions.add(version)
            
            return {
                "sample_size": len(sample['ids']),
                "sources": sources,
                "topics": topics, 
                "versions": list(versions),
                "latest_ingestion": sample['metadatas'][0].get('ingestion_date', 'unknown') if sample['metadatas'] else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"error": str(e)}
    
    def test_retrieval(self, test_queries: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """Test retrieval with common writing improvement queries."""
        if test_queries is None:
            test_queries = [
                "passive voice",
                "UI strings and capitalization", 
                "writing clear procedures",
                "inclusive language guidelines",
                "active voice examples",
                "button text capitalization",
                "avoiding wordy phrases"
            ]
        
        results = {}
        for query in test_queries:
            guidance = self.get_guidance(query, max_results=3, min_similarity=0.3)
            
            # Simplify results for testing
            results[query] = []
            for item in guidance:
                results[query].append({
                    "source": item["metadata"]["source"],
                    "title": item["metadata"]["title"],
                    "topic": item["metadata"]["topic"],
                    "similarity": round(item["similarity"], 3),
                    "preview": item["text"][:200] + "..." if len(item["text"]) > 200 else item["text"]
                })
        
        return results

# Convenience functions for direct use
def get_style_guidance(query: str, max_results: int = 6) -> List[Dict[str, Any]]:
    """Quick function to get style guidance."""
    retriever = StyleGuideRetriever()
    return retriever.get_guidance(query, max_results=max_results)

def build_guided_prompt(sentence: str, query: str) -> Optional[str]:
    """Quick function to build a prompt with style guide context."""
    retriever = StyleGuideRetriever()
    guidance = retriever.get_guidance(query)
    if guidance:
        return retriever.build_authoritative_prompt(sentence, guidance)
    return None

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the retriever
    retriever = StyleGuideRetriever()
    
    # Get collection info
    print("📊 Collection Info:")
    info = retriever.get_collection_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test retrieval
    print("\n🧪 Testing Retrieval:")
    test_results = retriever.test_retrieval()
    
    for query, results in test_results.items():
        print(f"\nQuery: '{query}' → {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['source']}] {result['title']} (sim: {result['similarity']})")
            print(f"     Preview: {result['preview']}")
    
    # Test prompt building
    print("\n📝 Testing Prompt Building:")
    test_sentence = "Mistakes were made by the user when the button was clicked."
    prompt = build_guided_prompt(test_sentence, "passive voice")
    
    if prompt:
        print("✅ Generated authoritative prompt:")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    else:
        print("❌ No guidance found for test query")
