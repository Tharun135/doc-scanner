# fastapi_app/models/pydantic_models.py
"""
Pydantic models for request/response validation.
Provides automatic validation and OpenAPI documentation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============= Request Models =============

class QueryRequest(BaseModel):
    """Request model for semantic search queries."""
    query: str = Field(..., description="The search query text", min_length=1)
    top_k: int = Field(5, description="Number of results to return", ge=1, le=20)
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    threshold: Optional[float] = Field(None, description="Similarity threshold (0-1)", ge=0, le=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How do I write clear technical documentation?",
                "top_k": 5,
                "filters": {"source": "manual.pdf"},
                "threshold": 0.7
            }
        }


class AnalyzeRequest(BaseModel):
    """Request model for document analysis."""
    text: Optional[str] = Field(None, description="Text content to analyze")
    file_id: Optional[str] = Field(None, description="ID of previously uploaded file")
    rules: Optional[List[str]] = Field(None, description="Specific rules to check")
    use_ai: bool = Field(False, description="Enable AI-powered suggestions")
    
    @validator('text', 'file_id')
    def check_at_least_one(cls, v, values):
        if not v and not values.get('file_id'):
            raise ValueError('Either text or file_id must be provided')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The system was configured by the administrator.",
                "rules": ["passive_voice", "word_choice"],
                "use_ai": True
            }
        }


class RuleCheckRequest(BaseModel):
    """Request model for rule-based checking."""
    text: str = Field(..., min_length=1)
    rule_ids: Optional[List[str]] = None
    severity_filter: Optional[str] = Field(None, pattern="^(error|warning|info)$")


class EmbedRequest(BaseModel):
    """Request model for generating embeddings."""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": ["First sentence to embed.", "Second sentence to embed."]
            }
        }


# ============= Response Models =============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    vector_store_count: int
    embedding_model: str


class ChunkMetadata(BaseModel):
    """Metadata for a document chunk."""
    source: str
    page: Optional[int] = None
    chunk_id: int
    token_count: Optional[int] = None
    type: Optional[str] = None


class SearchResult(BaseModel):
    """Single search result from vector store."""
    id: str
    text: str
    score: float = Field(..., description="Similarity score (lower is better for distance)")
    metadata: ChunkMetadata
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "manual_chunk_42",
                "text": "Use active voice to make your writing more direct...",
                "score": 0.23,
                "metadata": {
                    "source": "writing_guide.pdf",
                    "page": 15,
                    "chunk_id": 42,
                    "type": "pdf"
                }
            }
        }


class QueryResponse(BaseModel):
    """Response for semantic search queries."""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: float = Field(..., description="Query processing time in seconds")


class UploadResponse(BaseModel):
    """Response after file upload and ingestion."""
    filename: str
    file_id: str
    chunks_created: int
    chunks_ingested: int
    processing_time: float
    metadata: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "technical_manual.pdf",
                "file_id": "doc_12345",
                "chunks_created": 45,
                "chunks_ingested": 45,
                "processing_time": 2.34,
                "metadata": {
                    "type": "pdf",
                    "page_count": 120,
                    "size": "2.5 MB"
                }
            }
        }


class RuleFinding(BaseModel):
    """A single rule violation or suggestion."""
    rule_id: str
    rule_name: str
    severity: str  # error, warning, info
    message: str
    suggestion: Optional[str] = None
    line_number: Optional[int] = None
    char_offset: Optional[int] = None
    matched_text: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response for document analysis."""
    text_analyzed: str
    findings: List[RuleFinding]
    total_findings: int
    severity_counts: Dict[str, int]
    ai_suggestions: Optional[List[str]] = None
    processing_time: float


class StatsResponse(BaseModel):
    """Vector store statistics."""
    collection_name: str
    total_chunks: int
    unique_sources: int
    total_documents: int
    embedding_dimension: int
    last_updated: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime


# ============= Database Models (for future ORM) =============

class DocumentModel(BaseModel):
    """Model for stored documents."""
    id: str
    filename: str
    file_type: str
    upload_date: datetime
    chunk_count: int
    metadata: Dict[str, Any]


class RuleModel(BaseModel):
    """Model for writing rules."""
    id: str
    name: str
    description: str
    severity: str
    pattern: Optional[str] = None
    category: str
    enabled: bool = True
