from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer('all-MiniLM-L6-v2')

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

def chunk_text(text):
    if isinstance(text, list):
        text = " ".join(text)
    return [s.strip() for s in text.split('.') if len(s.strip()) > 20]

def ingest_documents(docs):
    # Ensure docs is processed properly based on input
    if isinstance(docs, str):
        chunks = chunk_text(docs)
    elif isinstance(docs, list):
        chunks = []
        for doc in docs:
            chunks.extend(chunk_text(doc))
    else:
        return
        
    if not chunks:
        return
        
    embeddings = model.encode(chunks)

    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        ids=[str(i) for i in range(len(chunks))]
    )
