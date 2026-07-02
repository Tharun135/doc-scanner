# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / WEB UI                           │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APP (Legacy)                         │
│  - Current UI and Routes                                        │
│  - Port 5000                                                    │
│  - Gradual Migration                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ Optional Proxy via fastapi_bridge.py
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI APP (New)                            │
│  Port 8000 | Automatic OpenAPI Docs | Async Ready              │
├─────────────────────────────────────────────────────────────────┤
│  Routes:                                                        │
│    /health              - Health checks & stats                 │
│    /upload              - Document ingestion                    │
│    /query               - Semantic search                       │
│    /query/rag           - RAG context retrieval                 │
│    /analyze             - Rule-based analysis                   │
└────────────┬──────────────────┬───────────────┬─────────────────┘
             │                  │               │
             ▼                  ▼               ▼
   ┌──────────────────┐ ┌──────────────┐ ┌─────────────────┐
   │   Embeddings     │ │ Vector Store │ │  Document       │
   │   Service        │ │  (ChromaDB)  │ │  Parser         │
   ├──────────────────┤ ├──────────────┤ ├─────────────────┤
   │ - SentenceTrans- │ │ - Persistent │ │ - PDF           │
   │   formers        │ │   Storage    │ │ - DOCX          │
   │ - Ollama Support │ │ - Cosine     │ │ - HTML          │
   │ - Batch Embed    │ │   Similarity │ │ - TXT/MD        │
   │ - 384-dim        │ │ - Metadata   │ │ - ZIP Archives  │
   └──────────────────┘ └──────────────┘ └─────────────────┘

```

## Data Flow: Document Upload

```
User uploads document.pdf
         │
         ▼
[POST /upload] Endpoint receives file
         │
         ▼
DocumentParser extracts & chunks text
         │
         ├─→ Chunk 1: "Use active voice..."
         ├─→ Chunk 2: "Avoid passive constructs..."
         └─→ Chunk 3: "Keep sentences short..."
         │
         ▼
EmbeddingModel generates vectors
         │
         ├─→ [0.23, -0.45, 0.12, ...] (384 dims)
         ├─→ [0.18, -0.32, 0.28, ...]
         └─→ [0.31, -0.21, 0.15, ...]
         │
         ▼
ChromaDB stores chunks + embeddings + metadata
         │
         └─→ {id, text, embedding, source, page, ...}
```

## Data Flow: Semantic Search

```
User query: "How to write clearly?"
         │
         ▼
[POST /query] Endpoint receives query
         │
         ▼
EmbeddingModel embeds query
         │
         └─→ Query vector: [0.28, -0.39, 0.19, ...]
         │
         ▼
ChromaDB finds similar vectors (cosine similarity)
         │
         ├─→ Result 1: distance=0.23 → Chunk 15
         ├─→ Result 2: distance=0.28 → Chunk 42
         └─→ Result 3: distance=0.31 → Chunk 3
         │
         ▼
Return formatted results with metadata
         │
         └─→ {results: [{text, score, metadata}, ...]}
```

## Data Flow: RAG Query

```
User asks: "Explain passive voice rules"
         │
         ▼
[POST /query/rag] Endpoint
         │
         ▼
Semantic Search (as above)
         │
         └─→ Top 3 relevant chunks
         │
         ▼
Format as LLM context
         │
         └─→ "[1] From style_guide.pdf, Page 42:
              Passive voice occurs when..."
         │
         ▼
Return context + sources
         │
         └─→ Use in LLM prompt for accurate answer
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  - Current Flask UI (HTML/JS)                                   │
│  - Future: React/Vue (optional)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                │
│  FastAPI 0.109  |  Pydantic 2.10  |  Uvicorn (ASGI)            │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                        │
│  Services: Embeddings | VectorStore | Parser | RuleEngine      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                                │
│  ChromaDB 1.0  |  SentenceTransformers 2.2  |  NLTK 3.8        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                              │
│  Local Filesystem  |  Vector DB (Persistent)  |  SQLite (Rules)│
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Docker Host                           │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Container: docscanner-fastapi                   │    │
│  │  Port: 8000                                      │    │
│  │  Volumes:                                        │    │
│  │    - ./chroma_db:/app/chroma_db                 │    │
│  │    - ./uploads:/app/uploads                     │    │
│  │    - ./logs:/app/logs                           │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Container: docscanner-flask (optional)          │    │
│  │  Port: 5000                                      │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Persistent Volumes  │
              │  - chroma_db/        │
              │  - uploads/          │
              │  - logs/             │
              └──────────────────────┘
```

## Scaling Architecture (Future)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (nginx/ALB)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────┐    ┌──────────┐   ┌──────────┐
      │ FastAPI  │    │ FastAPI  │   │ FastAPI  │
      │ Instance │    │ Instance │   │ Instance │
      │    1     │    │    2     │   │    3     │
      └────┬─────┘    └────┬─────┘   └────┬─────┘
           │               │              │
           └───────────────┼──────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   ChromaDB      │
                  │  (Shared/Cloud) │
                  └─────────────────┘
```

## Migration Path

```
Phase 1 (Week 1):           Phase 2 (Weeks 2-3):        Phase 3 (Week 4+):
┌─────────┐                 ┌─────────┐                  ┌─────────┐
│  Flask  │                 │  Flask  │────────┐         │  Flask  │
│  (5000) │                 │  (5000) │ Proxy  │         │   UI    │
└─────────┘                 └─────────┘        │         │  Only   │
                                     │          ▼         └────┬────┘
                            ┌─────────┐    ┌─────────┐       │
                            │ FastAPI │    │ FastAPI │       │
                            │ (8000)  │    │ (8000)  │       │
                            └─────────┘    └────┬────┘       │
                            Independent      Integrated      │
                            Testing         Features         ▼
                                                         ┌─────────┐
                                                         │ FastAPI │
                                                         │ Primary │
                                                         └─────────┘
```
