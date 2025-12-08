# fastapi_app/main.py
"""
FastAPI application entry point.
Main application with all routes, middleware, and configuration.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from fastapi_app.config import settings
from fastapi_app.routes import health, upload, query, analyze
from fastapi_app.services import get_embedder, get_vector_store

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(settings.LOG_FILE)] if settings.LOG_FILE else [])
    ]
)

logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Initialize resources on startup, cleanup on shutdown.
    """
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Startup: Initialize services
    try:
        logger.info("Initializing embedding model...")
        embedder = get_embedder(
            model_name=settings.EMBEDDING_MODEL,
            use_ollama=settings.USE_OLLAMA,
            ollama_url=settings.OLLAMA_URL,
            ollama_model=settings.OLLAMA_EMBED_MODEL
        )
        logger.info(f"✅ Embedding model loaded: {settings.EMBEDDING_MODEL}")
        logger.info(f"   Dimension: {embedder.get_dimension()}")
        
        logger.info("Initializing vector store...")
        vector_store = get_vector_store(
            persist_directory=settings.VECTOR_DB_DIR,
            collection_name=settings.VECTOR_COLLECTION_NAME
        )
        logger.info(f"✅ Vector store ready: {vector_store.count()} chunks")
        
        logger.info(f"🚀 Server starting on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    logger.info("Shutting down gracefully...")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **Doc Scanner RAG API** - Advanced document analysis with semantic search.
    
    Features:
    - 📄 Multi-format document ingestion (PDF, DOCX, HTML, TXT, MD, ZIP)
    - 🔍 Semantic search with vector embeddings
    - 🤖 RAG (Retrieval Augmented Generation) support
    - 📝 Rule-based document analysis
    - 🎯 AI-powered writing suggestions
    
    This API provides the backend for intelligent document processing and analysis.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Register routers
app.include_router(health.router)
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(analyze.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint with basic information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now().isoformat()
    }


# Additional utility endpoints
@app.get("/api/info", tags=["Info"])
async def api_info():
    """
    Get detailed API information and capabilities.
    """
    return {
        "api_version": settings.APP_VERSION,
        "capabilities": {
            "document_formats": settings.ALLOWED_EXTENSIONS,
            "max_upload_size_mb": settings.MAX_UPLOAD_SIZE // (1024 * 1024),
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
            "chunk_size": settings.CHUNK_SIZE,
            "semantic_search": True,
            "rag": True,
            "rule_engine": True,
            "ai_suggestions": bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)
        },
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "analyze": "/analyze",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
