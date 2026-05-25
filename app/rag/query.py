from sentence_transformers import SentenceTransformer
import chromadb
import os
import logging

logger = logging.getLogger(__name__)

# Lazy initialization of sentence transformer model to speed up startup
_model = None
def get_embedding_model():
    global _model
    if _model is None:
        logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

# ChromaDB Persistent Clients setup
# chroma_db holds document chunks and general knowledge/terminology
persist_path = os.path.join(os.getcwd(), 'chroma_db')
client = chromadb.PersistentClient(path=persist_path)

# docscanner_rules_db holds detailed style rules and remediations
rules_persist_path = os.path.join(os.getcwd(), 'docscanner_rules_db')
rules_client = chromadb.PersistentClient(path=rules_persist_path)

# Default collection for legacy RAG service compatibility
collection = client.get_or_create_collection("doc_chunks")

def retrieve_context(query):
    """Legacy RAG compatibility function"""
    try:
        model = get_embedding_model()
        query_embedding = model.encode([query])
        
        # Query default collection
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=3
        )
        if results and results.get("documents") and results["documents"][0]:
            return results["documents"][0]
        return []
    except Exception as e:
        logger.error(f"Error in retrieve_context: {e}")
        return []

def retrieve_terminology(query_sentence, n_results=3):
    """Retrieve relevant terminology guidelines/rules from knowledge collection"""
    try:
        knowledge_col = client.get_collection("docscanner_knowledge")
        model = get_embedding_model()
        query_embedding = model.encode([query_sentence])
        
        # Query specifically for terminology rules
        results = knowledge_col.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where={"issue_type": "terminology"}  # Filter for terminology if labeled
        )
        
        # If no terminology-specific items found, fallback to query without filter
        if not results or not results.get("documents") or not results["documents"][0]:
            results = knowledge_col.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            for doc, meta in zip(documents, metadatas):
                # Only return if relevant to terminology or general style
                formatted_results.append({
                    "content": doc,
                    "metadata": meta
                })
        return formatted_results
    except Exception as e:
        logger.warning(f"Failed to retrieve terminology: {e}")
        # Try returning from standard check if the collection wasn't loaded
        return []

def retrieve_reviewer_feedback(query_sentence, n_results=2):
    """Retrieve historical reviewer comments/feedback for similar sentences"""
    try:
        knowledge_col = client.get_collection("docscanner_knowledge")
        model = get_embedding_model()
        query_embedding = model.encode([query_sentence])
        
        # Search for learned corrections or reviewer feedback items
        results = knowledge_col.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where={"type": "learned_correction"}
        )
        
        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            for doc, meta in zip(documents, metadatas):
                formatted_results.append({
                    "original": meta.get("original", ""),
                    "corrected": meta.get("corrected", ""),
                    "feedback": meta.get("feedback", doc)
                })
        return formatted_results
    except Exception as e:
        logger.warning(f"Failed to retrieve reviewer feedback: {e}")
        return []

def retrieve_similar_manual_chunks(query_sentence, n_results=3):
    """Retrieve similar sentences/paragraphs from other indexed manuals for content reuse"""
    try:
        doc_col = client.get_collection("doc_chunks")
        model = get_embedding_model()
        query_embedding = model.encode([query_sentence])
        
        results = doc_col.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        formatted_results = []
        if results and results.get("documents") and results["documents"][0]:
            documents = results['documents'][0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            for doc, meta, dist in zip(documents, metadatas, distances):
                # Avoid returning the exact same sentence if queried
                similarity = 1.0 - float(dist)
                if doc.strip().lower() != query_sentence.strip().lower() and similarity > 0.4:
                    formatted_results.append({
                        "content": doc,
                        "source": meta.get("source", "Previous Manual"),
                        "similarity": round(similarity, 3)
                    })
        return formatted_results
    except Exception as e:
        logger.warning(f"Failed to retrieve manual chunks: {e}")
        return []

def retrieve_style_examples(rule_id, n_results=1):
    """Retrieve explicit style guide rule descriptions and Good/Bad examples"""
    try:
        rules_col = rules_client.get_collection("rule_remediations")
        
        # Direct lookup by ID is faster and more precise than embedding search
        results = rules_col.get(ids=[rule_id])
        
        if results and results.get("documents"):
            return {
                "rule_id": rule_id,
                "rule_text": results["documents"][0],
                "metadata": results["metadatas"][0] if results.get("metadatas") else {}
            }
        
        # Fallback to query
        model = get_embedding_model()
        query_embedding = model.encode([rule_id])
        query_results = rules_col.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        if query_results and query_results.get("documents") and query_results["documents"][0]:
            return {
                "rule_id": query_results["ids"][0][0],
                "rule_text": query_results["documents"][0][0],
                "metadata": query_results["metadatas"][0][0] if query_results.get("metadatas") else {}
            }
        return None
    except Exception as e:
        logger.warning(f"Failed to retrieve style examples for {rule_id}: {e}")
        return None
