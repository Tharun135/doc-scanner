#!/usr/bin/env python3
"""
Test the style guide retrieval with sample queries and show actual content
"""
import chromadb
from typing import List, Dict

def test_style_guide_retrieval():
    client = chromadb.PersistentClient(path="./db")
    collection = client.get_or_create_collection("style_guides")
    
    def query_guides(query: str, k=5, min_sim=0.3) -> List[Dict]:
        """Query the style guides collection"""
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where={"$and": [
                {"source_trust": "whitelist"}, 
                {"license": "permissive"}
            ]}
        )
        
        docs = []
        for i in range(len(results["ids"][0])):
            # ChromaDB returns cosine distances, convert to similarity
            similarity = 1 - results["distances"][0][i] if results["distances"] else None
            if similarity is None or similarity >= min_sim:
                docs.append({
                    "text": results["documents"][0][i],
                    "meta": results["metadatas"][0][i],
                    "similarity": similarity
                })
        return docs
    
    # Test queries that would be common in a doc scanner
    test_queries = [
        "writing instructions step by step procedures",
        "capitalization of UI elements and buttons", 
        "formatting URLs and web addresses",
        "inclusive language guidelines",
        "writing clear headings and titles",
        "formatting numbers and dates"
    ]
    
    print("🧪 Testing Style Guide Retrieval System")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        results = query_guides(query, k=3, min_sim=0.3)
        
        if not results:
            print("❌ No relevant guidance found")
            continue
            
        for i, result in enumerate(results, 1):
            meta = result["meta"]
            source = meta.get("source", "unknown")
            title = meta.get("title", "Untitled")
            topic = meta.get("topic", "general")
            similarity = result["similarity"]
            
            print(f"\n{i}. [{source.upper()}] {title}")
            print(f"   Topic: {topic} | Similarity: {similarity:.3f}")
            print(f"   Content preview:")
            # Show first 300 chars of content
            content_preview = result["text"][:300].strip()
            if len(result["text"]) > 300:
                content_preview += "..."
            print(f"   {content_preview}")
        
        print()

if __name__ == "__main__":
    test_style_guide_retrieval()
