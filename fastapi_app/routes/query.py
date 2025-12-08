# fastapi_app/routes/query.py
"""
Semantic search and RAG query endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi_app.models import QueryRequest, QueryResponse, SearchResult, ChunkMetadata
from fastapi_app.services import get_vector_store, get_embedder
from fastapi_app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
async def semantic_search(request: QueryRequest):
    """
    Perform semantic search across ingested documents.
    
    This endpoint:
    1. Generates embedding for the query
    2. Searches the vector store for similar chunks
    3. Returns top-k results with metadata
    """
    start_time = time.time()
    
    try:
        # Generate query embedding
        embedder = get_embedder(
            model_name=settings.EMBEDDING_MODEL,
            use_ollama=settings.USE_OLLAMA,
            ollama_url=settings.OLLAMA_URL,
            ollama_model=settings.OLLAMA_EMBED_MODEL
        )
        
        query_embedding = embedder.embed_query(request.query)
        
        # Search vector store
        vector_store = get_vector_store(
            persist_directory=settings.VECTOR_DB_DIR,
            collection_name=settings.VECTOR_COLLECTION_NAME
        )
        
        results = vector_store.query(
            query_embedding=query_embedding,
            top_k=min(request.top_k, settings.MAX_TOP_K),
            where=request.filters
        )
        
        # Format results
        search_results = []
        
        for doc, metadata, distance, doc_id in zip(
            results['documents'],
            results['metadatas'],
            results['distances'],
            results['ids']
        ):
            # Apply similarity threshold if specified
            if request.threshold and distance > (1 - request.threshold):
                continue
            
            # Create metadata object
            chunk_meta = ChunkMetadata(
                source=metadata.get('source', 'unknown'),
                page=metadata.get('page'),
                chunk_id=metadata.get('chunk_id', 0),
                token_count=metadata.get('token_count'),
                type=metadata.get('type')
            )
            
            search_result = SearchResult(
                id=doc_id,
                text=doc,
                score=round(distance, 4),
                metadata=chunk_meta
            )
            
            search_results.append(search_result)
        
        processing_time = time.time() - start_time
        
        response = QueryResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            processing_time=round(processing_time, 3)
        )
        
        logger.info(f"Query '{request.query[:50]}...' returned {len(search_results)} results in {processing_time:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/rag")
async def rag_query(request: QueryRequest):
    """
    RAG (Retrieval Augmented Generation) endpoint.
    
    This endpoint:
    1. Performs semantic search
    2. Constructs context from top results
    3. Returns results suitable for LLM prompting
    
    The frontend or LLM service can use this to build prompts.
    """
    try:
        # Perform semantic search
        search_response = await semantic_search(request)
        
        # Build context string from results
        context_parts = []
        for i, result in enumerate(search_response.results, 1):
            source = result.metadata.source
            page = f", Page {result.metadata.page}" if result.metadata.page else ""
            context_parts.append(
                f"[{i}] From {source}{page}:\n{result.text}\n"
            )
        
        context = "\n".join(context_parts)
        
        return {
            "query": request.query,
            "context": context,
            "sources": [
                {
                    "id": r.id,
                    "source": r.metadata.source,
                    "page": r.metadata.page,
                    "score": r.score
                }
                for r in search_response.results
            ],
            "total_results": search_response.total_results,
            "processing_time": search_response.processing_time
        }
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{chunk_id}")
async def find_similar_chunks(chunk_id: str, top_k: int = 5):
    """
    Find chunks similar to a specific chunk ID.
    Useful for exploring related content.
    """
    try:
        vector_store = get_vector_store()
        
        # Get the chunk
        chunk_data = vector_store.get_by_ids([chunk_id])
        
        if not chunk_data['documents']:
            raise HTTPException(status_code=404, detail=f"Chunk {chunk_id} not found")
        
        # Get embedding for this chunk and search
        embedder = get_embedder()
        chunk_text = chunk_data['documents'][0]
        chunk_embedding = embedder.embed_query(chunk_text)
        
        results = vector_store.query(
            query_embedding=chunk_embedding,
            top_k=top_k + 1  # +1 because it will include itself
        )
        
        # Filter out the original chunk
        similar_chunks = []
        for doc_id, doc, metadata, distance in zip(
            results['ids'],
            results['documents'],
            results['metadatas'],
            results['distances']
        ):
            if doc_id != chunk_id:
                similar_chunks.append({
                    "id": doc_id,
                    "text": doc,
                    "score": round(distance, 4),
                    "metadata": metadata
                })
        
        return {
            "chunk_id": chunk_id,
            "similar_chunks": similar_chunks[:top_k],
            "total": len(similar_chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to find similar chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
