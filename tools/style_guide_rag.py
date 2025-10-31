#!/usr/bin/env python3
"""
Style Guide RAG Integration for DocScanner
Provides whitelist-based authoritative guidance from Microsoft and Google style guides.
"""
import logging
from typing import List, Dict, Optional
import chromadb

logger = logging.getLogger(__name__)

class StyleGuideRAG:
    """
    Retrieval-Augmented Generation system for style guide content.
    Provides authoritative writing guidance from trusted sources.
    """
    
    def __init__(self, db_path: str = "./db", collection_name: str = "style_guides"):
        """Initialize the style guide RAG system."""
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to ChromaDB."""
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(self.collection_name)
            logger.info(f"Connected to style guides collection: {self.collection.count()} documents")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def retrieve_guidance(self, query: str, k: int = 5, min_similarity: float = 0.35) -> List[Dict]:
        """
        Retrieve authoritative style guidance for a query.
        
        Args:
            query: The text to find guidance for
            k: Maximum number of results to return
            min_similarity: Minimum similarity threshold (0-1)
            
        Returns:
            List of guidance documents with metadata and similarity scores
        """
        try:
            # Query only trusted, permissive sources
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where={"$and": [
                    {"source_trust": "whitelist"}, 
                    {"license": "permissive"}
                ]}
            )
            
            guidance = []
            for i in range(len(results["ids"][0])):
                # Convert distance to similarity (ChromaDB returns cosine distance)
                similarity = 1 - results["distances"][0][i] if results["distances"] else 0
                
                if similarity >= min_similarity:
                    guidance.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": similarity,
                        "source": results["metadatas"][0][i].get("source", "unknown"),
                        "title": results["metadatas"][0][i].get("title", "Untitled"),
                        "topic": results["metadatas"][0][i].get("topic", "general"),
                    })
            
            # Sort by similarity (highest first)
            guidance.sort(key=lambda x: x["similarity"], reverse=True)
            
            logger.debug(f"Retrieved {len(guidance)} guidance documents for: '{query}'")
            return guidance
            
        except Exception as e:
            logger.error(f"Failed to retrieve guidance: {e}")
            return []
    
    def build_guidance_prompt(self, sentence: str, max_guidance: int = 3) -> Optional[str]:
        """
        Build a prompt with authoritative guidance context for LLM rewriting.
        
        Args:
            sentence: The sentence to be improved
            max_guidance: Maximum number of guidance snippets to include
            
        Returns:
            Formatted prompt with authoritative context, or None if no guidance found
        """
        guidance = self.retrieve_guidance(sentence, k=max_guidance * 2, min_similarity=0.3)
        
        if not guidance:
            return None
        
        # Build context from top guidance
        context_items = []
        for item in guidance[:max_guidance]:
            source = item["source"].upper()
            title = item["title"]
            text_preview = item["text"][:500].strip()
            if len(item["text"]) > 500:
                text_preview += "..."
                
            context_items.append(f"**[{source}] {title}**\n{text_preview}")
        
        context = "\n\n".join(context_items)
        
        prompt = f"""You are a technical writing editor. Follow the authoritative style guidance below.

**AUTHORITATIVE GUIDANCE (from trusted style guides):**
{context}

**SENTENCE TO IMPROVE:**
"{sentence}"

**REQUIREMENTS:**
- Keep the meaning intact
- Apply the guidance from the trusted sources above
- Use active voice, clear language, and concise sentences
- Do not alter product names, UI labels, code, or URLs
- If the sentence is already compliant, return it unchanged

**TASK:**
Provide a single improved rewrite that follows the guidance above. Then give a brief rationale referencing the specific guidance used.

Return as JSON: {{"rewrite": "...", "rationale": "..."}}"""

        return prompt
    
    def get_guidance_summary(self, query: str) -> str:
        """Get a human-readable summary of available guidance for a query."""
        guidance = self.retrieve_guidance(query, k=3, min_similarity=0.3)
        
        if not guidance:
            return f"No specific guidance found for: '{query}'"
        
        summary_parts = [f"Found {len(guidance)} guidance items for: '{query}'\n"]
        
        for i, item in enumerate(guidance, 1):
            source = item["source"].upper()
            title = item["title"]
            similarity = item["similarity"]
            topic = item["topic"]
            
            summary_parts.append(
                f"{i}. [{source}] {title}\n"
                f"   Topic: {topic} | Relevance: {similarity:.1%}\n"
                f"   Preview: {item['text'][:150]}...\n"
            )
        
        return "\n".join(summary_parts)


def test_integration():
    """Test the style guide integration with sample sentences."""
    rag = StyleGuideRAG()
    
    test_sentences = [
        "Click on the Submit button to save your changes.",
        "Users can find this option in Settings.",
        "The file will be downloaded to your computer.",
        "Follow these steps to complete the setup.",
    ]
    
    print("🧪 Testing Style Guide RAG Integration")
    print("=" * 50)
    
    for sentence in test_sentences:
        print(f"\n📝 Original: '{sentence}'")
        
        # Get guidance
        guidance = rag.retrieve_guidance(sentence, k=2)
        if guidance:
            print(f"✅ Found {len(guidance)} guidance items:")
            for item in guidance:
                source = item["source"].upper()
                title = item["title"]
                similarity = item["similarity"]
                print(f"   • [{source}] {title} (relevance: {similarity:.1%})")
        else:
            print("❌ No relevant guidance found")
        
        # Build prompt
        prompt = rag.build_guidance_prompt(sentence, max_guidance=2)
        if prompt:
            print("✅ Generated guidance-based prompt")
        else:
            print("❌ No prompt generated")


if __name__ == "__main__":
    test_integration()
