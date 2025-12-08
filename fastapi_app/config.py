# fastapi_app/config.py
"""
Configuration management using Pydantic Settings.
Loads from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Settings
    APP_NAME: str = "Doc Scanner RAG API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: list = [".txt", ".pdf", ".docx", ".doc", ".md", ".html", ".adoc", ".zip"]
    
    # Vector Database Settings
    VECTOR_DB_DIR: str = "./chroma_db"
    VECTOR_COLLECTION_NAME: str = "doc_chunks"
    CHROMA_PERSIST: bool = True
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # for all-MiniLM-L6-v2
    CHUNK_SIZE: int = 300  # tokens
    CHUNK_OVERLAP: int = 50  # tokens
    
    # LLM Settings (optional)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_API_URL: Optional[str] = None
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_MAX_TOKENS: int = 1000
    LLM_TEMPERATURE: float = 0.7
    
    # Ollama Settings (if using local LLM)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    USE_OLLAMA: bool = False
    
    # Search Settings
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Rule Engine Settings
    RULES_DB_PATH: str = "./suggestion_metrics.db"
    RULES_CONFIG_DIR: str = "./config"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
    os.makedirs(settings.RULES_CONFIG_DIR, exist_ok=True)
    if settings.LOG_FILE:
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)


ensure_directories()
