# Doc Scanner FastAPI Migration Guide

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
# Create virtual environment (if not already created)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install FastAPI dependencies
pip install -r fastapi_requirements.txt

# Download NLTK data (required for sentence tokenization)
python -c "import nltk; nltk.download('punkt')"
```

### 2. Configure Environment

```powershell
# Copy example env file
Copy-Item .env.fastapi.example .env

# Edit .env with your settings
notepad .env
```

### 3. Run the Server

```powershell
# Method 1: Using the startup script
python run_fastapi.py

# Method 2: Using uvicorn directly
uvicorn fastapi_app.main:app --reload --port 8000

# Method 3: Using the main module
python -m fastapi_app.main
```

### 4. Access the API

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/api/info

## 📁 Architecture

```
fastapi_app/
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── models/
│   ├── __init__.py
│   └── pydantic_models.py  # Request/response models
├── routes/
│   ├── __init__.py
│   ├── health.py           # Health and status endpoints
│   ├── upload.py           # Document upload/ingestion
│   ├── query.py            # Semantic search/RAG
│   └── analyze.py          # Document analysis
└── services/
    ├── __init__.py
    ├── embeddings.py       # Embedding generation
    ├── vector_store.py     # ChromaDB management
    └── parser.py           # Document parsing
```

## 🎯 Key Features

### 1. **Semantic Search**
- Upload documents in multiple formats
- Automatic chunking and embedding
- Vector similarity search
- Metadata filtering

### 2. **RAG Support**
- Retrieve relevant context for queries
- Format results for LLM prompting
- Source tracking and citations

### 3. **Document Analysis**
- Rule-based checking (integrates with existing rules)
- AI-powered suggestions
- Batch processing

### 4. **Multiple Embedding Options**
- Local: SentenceTransformers
- Local: Ollama
- Cloud: OpenAI (optional)

## 📊 API Endpoints

### Health & Status
- `GET /health` - Health check
- `GET /health/stats` - Detailed statistics
- `GET /health/ready` - Readiness probe

### Upload
- `POST /upload` - Upload and ingest document
- `DELETE /upload/{file_id}` - Delete document
- `GET /upload/list` - List all documents

### Query
- `POST /query` - Semantic search
- `POST /query/rag` - RAG-formatted query
- `GET /query/similar/{chunk_id}` - Find similar chunks

### Analysis
- `POST /analyze` - Analyze text with rules
- `GET /analyze/rules` - List available rules
- `POST /analyze/batch` - Batch analysis

## 🔧 Configuration Options

Key environment variables in `.env`:

```bash
# Server
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=false

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=300
CHUNK_OVERLAP=50

# Vector Store
VECTOR_DB_DIR=./chroma_db
VECTOR_COLLECTION_NAME=doc_chunks

# Optional: Ollama
USE_OLLAMA=false
OLLAMA_URL=http://localhost:11434

# Optional: OpenAI
OPENAI_API_KEY=your-key-here
```

## 📝 Example Usage

### Upload a Document

```python
import requests

with open("manual.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
    
print(response.json())
# Output: {"filename": "manual.pdf", "chunks_ingested": 45, ...}
```

### Query the Knowledge Base

```python
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "How do I write clear documentation?",
        "top_k": 5
    }
)

results = response.json()
for result in results["results"]:
    print(f"Source: {result['metadata']['source']}")
    print(f"Text: {result['text'][:100]}...")
    print(f"Score: {result['score']}\n")
```

### RAG Query (for LLM)

```python
response = requests.post(
    "http://localhost:8000/query/rag",
    json={
        "query": "Explain passive voice rules",
        "top_k": 3
    }
)

data = response.json()
print("Context for LLM:")
print(data["context"])
print("\nSources:", data["sources"])
```

## 🔄 Migration from Flask

### Phase 1: Run Both APIs in Parallel
1. Keep Flask running on port 5000
2. Start FastAPI on port 8000
3. Test FastAPI endpoints independently

### Phase 2: Integrate Rule Engine
1. Import existing rule engine from `app/`
2. Wire into `analyze.py` endpoints
3. Test rule checking functionality

### Phase 3: Point UI to FastAPI
Update your UI to call FastAPI endpoints:
- Old: `http://localhost:5000/api/analyze`
- New: `http://localhost:8000/analyze`

### Phase 4: Full Cutover
1. Migrate remaining Flask features
2. Update all frontend code
3. Deprecate Flask server

## 🧪 Testing

### Manual Testing with curl

```powershell
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST http://localhost:8000/upload `
  -F "file=@test.pdf"

# Query
curl -X POST http://localhost:8000/query `
  -H "Content-Type: application/json" `
  -d '{"query": "technical writing", "top_k": 5}'
```

### Using the Interactive Docs
Visit http://localhost:8000/docs and use the "Try it out" feature for each endpoint.

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Change port in .env or run with:
uvicorn fastapi_app.main:app --port 8001
```

### Missing Dependencies
```powershell
pip install -r fastapi_requirements.txt
```

### NLTK Data Missing
```powershell
python -c "import nltk; nltk.download('punkt')"
```

### ChromaDB Errors
```powershell
# Clear vector database if corrupted
Remove-Item -Recurse -Force ./chroma_db
```

## 📚 Next Steps

1. **Integrate Existing Rules**: Wire your Flask rule engine into the analyze endpoints
2. **Add LLM Integration**: Implement AI suggestions with OpenAI/Anthropic
3. **Add Authentication**: Implement API key or JWT authentication
4. **Add Caching**: Use Redis for query caching
5. **Add Monitoring**: Integrate Prometheus/Grafana
6. **Containerize**: Create Docker image for deployment

## 🎓 Learn More

- FastAPI Docs: https://fastapi.tiangolo.com/
- ChromaDB Docs: https://docs.trychroma.com/
- SentenceTransformers: https://www.sbert.net/

---

**Ready to transform your Doc Scanner? Start the server and visit `/docs` to explore!** 🚀
