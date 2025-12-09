# fastapi_app/routes/health.py
"""
Health check and system status endpoints.
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from fastapi_app.models import HealthResponse
from fastapi_app.services import get_vector_store, get_embedder
from fastapi_app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns system status and basic statistics.
    """
    try:
        vector_store = get_vector_store(
            persist_directory=settings.VECTOR_DB_DIR,
            collection_name=settings.VECTOR_COLLECTION_NAME
        )
        
        embedder = get_embedder(
            model_name=settings.EMBEDDING_MODEL,
            use_ollama=settings.USE_OLLAMA,
            ollama_url=settings.OLLAMA_URL,
            ollama_model=settings.OLLAMA_EMBED_MODEL
        )
        
        chunk_count = vector_store.count()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            version=settings.APP_VERSION,
            vector_store_count=chunk_count,
            embedding_model=settings.EMBEDDING_MODEL
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            version=settings.APP_VERSION,
            vector_store_count=0,
            embedding_model=settings.EMBEDDING_MODEL
        )


@router.get("/stats")
async def get_stats():
    """
    Get detailed system statistics.
    """
    try:
        vector_store = get_vector_store(
            persist_directory=settings.VECTOR_DB_DIR,
            collection_name=settings.VECTOR_COLLECTION_NAME
        )
        
        stats = vector_store.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "config": {
                "embedding_model": settings.EMBEDDING_MODEL,
                "chunk_size": settings.CHUNK_SIZE,
                "chunk_overlap": settings.CHUNK_OVERLAP,
                "max_upload_size": settings.MAX_UPLOAD_SIZE,
                "vector_db_dir": settings.VECTOR_DB_DIR
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes-style readiness probe.
    Checks if the service can handle requests.
    """
    try:
        # Check if vector store is accessible
        vector_store = get_vector_store()
        vector_store.count()
        
        # Check if embedder is loaded
        embedder = get_embedder()
        test_embedding = embedder.embed_query("test")
        
        if len(test_embedding) > 0:
            return {"ready": True}
        else:
            return {"ready": False, "reason": "Embedder not working"}
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "reason": str(e)}
