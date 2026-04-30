from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client()
collection = client.get_or_create_collection("docs")

def retrieve_context(query):
    query_embedding = model.encode([query])

    from app.services.rag_service import CONFIG
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=CONFIG["rag_top_k"]
    )

    return results["documents"]
