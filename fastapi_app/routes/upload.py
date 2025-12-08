# fastapi_app/routes/upload.py
"""
File upload and document ingestion endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi_app.models import UploadResponse
from fastapi_app.services import get_vector_store, get_embedder, DocumentParser
from fastapi_app.config import settings
import logging
import os
import time
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and ingest a document into the vector store.
    
    Supported formats: PDF, DOCX, HTML, TXT, MD, ZIP
    
    Process:
    1. Save uploaded file
    2. Parse and chunk the document
    3. Generate embeddings
    4. Store in vector database
    """
    start_time = time.time()
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Generate unique file ID
    file_id = f"doc_{uuid.uuid4().hex[:12]}"
    
    # Save uploaded file
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    try:
        # Write file to disk
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {safe_filename} ({len(content)} bytes)")
        
        # Parse and chunk the document
        parser = DocumentParser(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        chunks = parser.parse_and_chunk(file_path)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No content could be extracted from the file"
            )
        
        logger.info(f"Created {len(chunks)} chunks from {file.filename}")
        
        # Generate embeddings
        embedder = get_embedder(
            model_name=settings.EMBEDDING_MODEL,
            use_ollama=settings.USE_OLLAMA,
            ollama_url=settings.OLLAMA_URL,
            ollama_model=settings.OLLAMA_EMBED_MODEL
        )
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = embedder.embed_texts(texts, show_progress=True)
        
        # Prepare data for vector store
        ids = [chunk['id'] for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = {
                'source': chunk['source'],
                'file_id': file_id,
                'chunk_id': chunk['chunk_id'],
                'token_count': chunk.get('token_count', 0)
            }
            
            # Add optional fields
            if 'page' in chunk:
                metadata['page'] = chunk['page']
            if 'metadata' in chunk and 'type' in chunk['metadata']:
                metadata['type'] = chunk['metadata']['type']
            
            metadatas.append(metadata)
        
        # Store in vector database
        vector_store = get_vector_store(
            persist_directory=settings.VECTOR_DB_DIR,
            collection_name=settings.VECTOR_COLLECTION_NAME
        )
        
        vector_store.add_chunks(ids, texts, embeddings, metadatas)
        
        processing_time = time.time() - start_time
        
        # Get file metadata
        file_metadata = chunks[0].get('metadata', {}) if chunks else {}
        
        response = UploadResponse(
            filename=file.filename,
            file_id=file_id,
            chunks_created=len(chunks),
            chunks_ingested=len(chunks),
            processing_time=round(processing_time, 2),
            metadata=file_metadata
        )
        
        logger.info(f"Successfully ingested {file.filename} in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to process upload: {e}")
        
        # Cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


@router.delete("/{file_id}")
async def delete_document(file_id: str):
    """
    Delete a document and all its chunks from the vector store.
    """
    try:
        vector_store = get_vector_store()
        
        # Delete all chunks with this file_id
        vector_store.delete_by_source(file_id)
        
        # Also try to delete the physical file
        upload_dir = Path(settings.UPLOAD_DIR)
        for file_path in upload_dir.glob(f"{file_id}_*"):
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path.name}")
        
        return {
            "status": "success",
            "message": f"Deleted document {file_id} and all associated chunks"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents():
    """
    List all uploaded documents.
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        
        documents = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                # Extract file_id from filename (format: {file_id}_{original_name})
                parts = file_path.name.split('_', 1)
                file_id = parts[0]
                original_name = parts[1] if len(parts) > 1 else file_path.name
                
                documents.append({
                    "file_id": file_id,
                    "filename": original_name,
                    "size": file_path.stat().st_size,
                    "upload_date": file_path.stat().st_mtime
                })
        
        return {
            "status": "success",
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
