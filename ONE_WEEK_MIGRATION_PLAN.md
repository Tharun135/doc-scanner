# 📅 One-Week FastAPI Migration Plan

## Overview
This plan guides you through adding vector search capabilities and migrating to FastAPI over 7 days, with specific daily tasks and validation steps.

---

## 🎯 Day 1: Setup and Prototype Embeddings

### Goals
- Install all dependencies
- Test embedding generation
- Verify vector store functionality
- Ingest sample documents

### Tasks

#### 1. Environment Setup (30 min)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install FastAPI dependencies
pip install -r fastapi_requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt')"

# Verify installations
python -c "import fastapi, chromadb, sentence_transformers; print('✅ All imports successful')"
```

#### 2. Configure Environment (15 min)
```powershell
# Copy and customize env file
Copy-Item .env.fastapi.example .env
notepad .env
```

Set these key values:
- `FASTAPI_PORT=8000`
- `VECTOR_DB_DIR=./chroma_db`
- `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`

#### 3. Test Embedding Generation (30 min)
Create `test_embeddings.py`:
```python
from fastapi_app.services.embeddings import EmbeddingModel

embedder = EmbeddingModel()
texts = ["This is a test sentence.", "Another test sentence."]
embeddings = embedder.embed_texts(texts)

print(f"✅ Generated {len(embeddings)} embeddings")
print(f"   Dimension: {len(embeddings[0])}")
assert len(embeddings) == 2
assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2
print("✅ Embedding test passed!")
```

Run: `python test_embeddings.py`

#### 4. Test Vector Store (30 min)
Create `test_vector_store.py`:
```python
from fastapi_app.services.vector_store import ChromaManager
from fastapi_app.services.embeddings import EmbeddingModel

# Initialize
store = ChromaManager(persist_directory="./test_chroma_db")
embedder = EmbeddingModel()

# Add test data
texts = [
    "Use active voice for clarity.",
    "Passive voice should be avoided.",
    "Keep sentences short and simple."
]
embeddings = embedder.embed_texts(texts)
ids = [f"test_{i}" for i in range(len(texts))]
metadatas = [{"source": "test", "chunk_id": i} for i in range(len(texts))]

store.add_chunks(ids, texts, embeddings, metadatas)

# Query
query_emb = embedder.embed_query("How to write clear sentences?")
results = store.query(query_emb, top_k=2)

print(f"✅ Query returned {len(results['documents'])} results")
for doc, dist in zip(results['documents'], results['distances']):
    print(f"   - {doc[:50]}... (score: {dist:.3f})")

print("✅ Vector store test passed!")
```

Run: `python test_vector_store.py`

#### 5. Ingest Sample Documents (1 hour)
```powershell
# Start FastAPI server
python run_fastapi.py

# In another terminal, upload 3 small test documents
curl -X POST http://localhost:8000/upload `
  -F "file=@data/test_document.txt"
```

### Success Criteria
- ✅ All dependencies installed
- ✅ Embeddings generate successfully
- ✅ Vector store accepts and queries data
- ✅ 3 documents ingested with chunks in vector DB

---

## 🎯 Day 2: Document Parser and Chunking

### Goals
- Implement robust multi-format parser
- Test chunking strategies
- Handle edge cases
- Add unit tests

### Tasks

#### 1. Test PDF Parsing (45 min)
```python
from fastapi_app.services.parser import DocumentParser

parser = DocumentParser(chunk_size=300, chunk_overlap=50)

# Test with your existing PDF
chunks = parser.parse_and_chunk("data/test_manual.pdf")

print(f"✅ Parsed PDF: {len(chunks)} chunks")
for i, chunk in enumerate(chunks[:3]):
    print(f"\nChunk {i}:")
    print(f"  ID: {chunk['id']}")
    print(f"  Tokens: {chunk.get('token_count', 'N/A')}")
    print(f"  Text: {chunk['text'][:100]}...")
```

#### 2. Test DOCX and HTML (45 min)
```python
# Test DOCX
docx_chunks = parser.parse_and_chunk("data/test_doc.docx")
print(f"✅ DOCX: {len(docx_chunks)} chunks")

# Test HTML
html_chunks = parser.parse_and_chunk("data/test.html")
print(f"✅ HTML: {len(html_chunks)} chunks")
```

#### 3. Test ZIP Archives (30 min)
Create a test ZIP with multiple file types and parse it.

#### 4. Add Unit Tests (1 hour)
Create `tests/test_parser.py`:
```python
import pytest
from fastapi_app.services.parser import DocumentParser

def test_chunk_text():
    parser = DocumentParser(chunk_size=50, chunk_overlap=10)
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = parser.chunk_text(text)
    
    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    print(f"✅ Created {len(chunks)} chunks")

def test_parse_text_file():
    parser = DocumentParser()
    result = parser.parse_file("data/test_document.txt")
    
    assert 'text' in result
    assert 'metadata' in result
    assert len(result['text']) > 0
    print("✅ Text file parsing works")

# Run with: pytest tests/test_parser.py -v
```

### Success Criteria
- ✅ All file formats parse correctly
- ✅ Chunking respects size and overlap
- ✅ Unit tests pass
- ✅ Edge cases handled (empty files, large files)

---

## 🎯 Day 3: Full Pipeline Integration

### Goals
- Wire parser → embedder → vector store
- Test end-to-end ingestion
- Optimize performance
- Test with large document (200+ pages)

### Tasks

#### 1. Test Full Upload Pipeline (1 hour)
```powershell
# Start server
python run_fastapi.py

# Upload various file types
curl -X POST http://localhost:8000/upload -F "file=@test.pdf"
curl -X POST http://localhost:8000/upload -F "file=@test.docx"
curl -X POST http://localhost:8000/upload -F "file=@test.html"
```

Check response times and chunk counts.

#### 2. Test with Large Document (1 hour)
Upload a 200-page PDF and monitor:
- Parsing time
- Embedding generation time
- Vector store insertion time
- Memory usage

```python
import requests
import time

start = time.time()
with open("large_manual.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
end = time.time()

print(f"Upload took {end-start:.2f} seconds")
print(f"Chunks ingested: {response.json()['chunks_ingested']}")
```

#### 3. Tune Chunk Size (1 hour)
Experiment with different chunk sizes:
- 150 tokens
- 300 tokens (default)
- 500 tokens

Test retrieval quality with each setting.

#### 4. Add Batch Processing (1 hour)
Optimize embedder for batch processing:
```python
# In embeddings.py, ensure batch_embed is used
embeddings = embedder.batch_embed(texts, batch_size=64)
```

### Success Criteria
- ✅ Full pipeline works end-to-end
- ✅ 200+ page document ingests successfully
- ✅ Processing time < 5 minutes for large docs
- ✅ Optimal chunk size determined

---

## 🎯 Day 4: Semantic Query and LLM Integration

### Goals
- Test semantic search thoroughly
- Implement RAG endpoint
- Add basic LLM wrapper
- Test end-to-end RAG flow

### Tasks

#### 1. Test Semantic Search (1 hour)
```python
import requests

# Query examples
queries = [
    "How to write clear technical documentation?",
    "What are passive voice rules?",
    "Best practices for sentence structure"
]

for query in queries:
    response = requests.post(
        "http://localhost:8000/query",
        json={"query": query, "top_k": 5}
    )
    results = response.json()
    
    print(f"\nQuery: {query}")
    print(f"Results: {results['total_results']}")
    for r in results['results'][:2]:
        print(f"  - {r['metadata']['source']} (score: {r['score']})")
        print(f"    {r['text'][:80]}...")
```

#### 2. Test RAG Endpoint (1 hour)
```python
response = requests.post(
    "http://localhost:8000/query/rag",
    json={"query": "Explain passive voice", "top_k": 3}
)

data = response.json()
print("Context for LLM:")
print(data["context"])
print("\nSources:", len(data["sources"]))
```

#### 3. Add Simple LLM Wrapper (2 hours)
Create `fastapi_app/services/llm_suggester.py`:
```python
import os
from openai import OpenAI

class LLMSuggester:
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def get_suggestions(self, text: str, context: str) -> list[str]:
        prompt = f"""Given this context from documentation:
{context}

Analyze this text and provide suggestions:
{text}

Provide 3 specific suggestions for improvement."""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return [response.choices[0].message.content]
```

#### 4. Test Full RAG Flow (1 hour)
UI Query → Semantic Search → Context Retrieval → LLM Prompt → Answer

### Success Criteria
- ✅ Semantic search returns relevant results
- ✅ RAG endpoint formats context correctly
- ✅ LLM integration works (if API key available)
- ✅ End-to-end flow tested

---

## 🎯 Day 5: Modularization and API Documentation

### Goals
- Refactor into clean services
- Add dependency injection
- Complete Pydantic models
- Verify OpenAPI docs

### Tasks

#### 1. Dependency Injection Pattern (2 hours)
Refactor to use FastAPI dependencies:
```python
from fastapi import Depends

def get_embedder_dep():
    return get_embedder()

def get_vector_store_dep():
    return get_vector_store()

@router.post("/query")
async def query(
    request: QueryRequest,
    embedder: EmbeddingModel = Depends(get_embedder_dep),
    store: ChromaManager = Depends(get_vector_store_dep)
):
    # Use injected dependencies
    ...
```

#### 2. Complete Pydantic Models (1 hour)
Ensure all request/response models have:
- Proper validation
- Example values
- Clear descriptions

#### 3. Test OpenAPI Documentation (30 min)
Visit `http://localhost:8000/docs` and verify:
- All endpoints documented
- Request/response schemas clear
- "Try it out" works for each endpoint
- Examples are helpful

#### 4. Add Error Handling (1 hour)
Test error cases:
- Invalid file uploads
- Missing required fields
- Vector store failures
- Embedding errors

### Success Criteria
- ✅ Clean dependency injection
- ✅ All models validated with examples
- ✅ OpenAPI docs complete and accurate
- ✅ Error handling robust

---

## 🎯 Day 6: Integrate with Flask UI

### Goals
- Run both APIs in parallel
- Update Flask UI to call FastAPI
- Test all features from UI
- Add smoke tests

### Tasks

#### 1. Run Both Servers (15 min)
```powershell
# Terminal 1: Flask
python run.py

# Terminal 2: FastAPI
python run_fastapi.py
```

#### 2. Update Flask Routes (2 hours)
In your Flask `app.py`, add proxy functions:
```python
import requests

FASTAPI_URL = "http://localhost:8000"

@main.route('/api/upload_new', methods=['POST'])
def upload_to_fastapi():
    file = request.files['file']
    response = requests.post(
        f"{FASTAPI_URL}/upload",
        files={"file": file}
    )
    return jsonify(response.json())

@main.route('/api/query_semantic', methods=['POST'])
def query_fastapi():
    data = request.get_json()
    response = requests.post(
        f"{FASTAPI_URL}/query",
        json=data
    )
    return jsonify(response.json())
```

#### 3. Update Frontend JavaScript (2 hours)
Update API calls to use new endpoints:
```javascript
// Old
fetch('/api/upload', {method: 'POST', body: formData})

// New (testing)
fetch('/api/upload_new', {method: 'POST', body: formData})
```

#### 4. Smoke Tests (1 hour)
Test core workflows:
- Upload document via UI → verify in FastAPI
- Query semantic search via UI → verify results
- Analyze text via UI → verify findings

### Success Criteria
- ✅ Both APIs running simultaneously
- ✅ Flask UI can call FastAPI endpoints
- ✅ All core features work from UI
- ✅ No regressions in existing functionality

---

## 🎯 Day 7: Hardening and Deployment Prep

### Goals
- Add comprehensive tests
- Dockerize FastAPI
- Add logging and monitoring
- Create deployment documentation

### Tasks

#### 1. Add Integration Tests (2 hours)
Create `tests/test_integration.py`:
```python
import pytest
from fastapi.testclient import TestClient
from fastapi_app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_and_query():
    # Upload
    with open("test.txt", "rb") as f:
        response = client.post("/upload", files={"file": f})
    assert response.status_code == 200
    
    # Query
    response = client.post("/query", json={"query": "test", "top_k": 5})
    assert response.status_code == 200
    assert "results" in response.json()
```

Run: `pytest tests/ -v --cov=fastapi_app`

#### 2. Create Dockerfile (1 hour)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY fastapi_requirements.txt .
RUN pip install --no-cache-dir -r fastapi_requirements.txt

COPY fastapi_app/ ./fastapi_app/
COPY run_fastapi.py .

RUN python -c "import nltk; nltk.download('punkt')"

EXPOSE 8000

CMD ["python", "run_fastapi.py"]
```

Build and test:
```powershell
docker build -t docscanner-fastapi -f Dockerfile.fastapi .
docker run -p 8000:8000 docscanner-fastapi
```

#### 3. Add docker-compose.yml (30 min)
```yaml
version: '3.8'

services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./uploads:/app/uploads
    environment:
      - VECTOR_DB_DIR=/app/chroma_db
      - UPLOAD_DIR=/app/uploads
```

#### 4. Add Logging and Monitoring (1 hour)
- Configure structured logging
- Add request timing middleware
- Add health check endpoint for monitoring

#### 5. Documentation (1 hour)
Update README with:
- Quickstart guide
- API endpoint documentation
- Deployment instructions
- Troubleshooting guide

### Success Criteria
- ✅ All tests pass
- ✅ Docker image builds and runs
- ✅ Logging configured
- ✅ Documentation complete
- ✅ Ready for staging deployment

---

## 📊 Success Metrics

After completing all 7 days, you should have:

### Functionality
- ✅ Multi-format document ingestion (PDF, DOCX, HTML, TXT, ZIP)
- ✅ Semantic search with 384-dimensional embeddings
- ✅ RAG-ready context retrieval
- ✅ Rule-based analysis (integrated from Flask)
- ✅ FastAPI running alongside Flask

### Performance
- ✅ <5 min to ingest 200-page document
- ✅ <500ms for semantic search queries
- ✅ <100ms for health checks
- ✅ Efficient batch embedding processing

### Quality
- ✅ 80%+ test coverage
- ✅ Comprehensive error handling
- ✅ Clean, modular architecture
- ✅ Full OpenAPI documentation

### Deployment
- ✅ Dockerized application
- ✅ docker-compose configuration
- ✅ CI/CD ready
- ✅ Production-ready logging

---

## 🚀 Beyond Week 1

### Week 2-3: Full Migration
- Migrate all Flask features to FastAPI
- Update all UI calls to FastAPI
- Add authentication/authorization
- Performance optimization

### Week 4: Advanced Features
- Multi-document cross-search
- Advanced RAG with re-ranking
- Streaming responses
- WebSocket support for real-time analysis

### Month 2: Production Hardening
- Load testing
- Security audit
- Monitoring and alerting
- Auto-scaling setup

---

## 💡 Pro Tips

1. **Test early, test often**: Run tests after each major change
2. **Keep Flask running**: Don't shut down Flask until FastAPI is proven
3. **Monitor performance**: Use logging to track bottlenecks
4. **Start small**: Test with small documents before large ones
5. **Version control**: Commit after each day's work
6. **Documentation**: Keep notes on what works and what doesn't

---

## 🆘 Troubleshooting

### Common Issues

**Import Errors**
```powershell
pip install -r fastapi_requirements.txt --upgrade
```

**Vector Store Errors**
```powershell
Remove-Item -Recurse -Force ./chroma_db
# Restart and re-ingest
```

**Out of Memory**
- Reduce `CHUNK_SIZE`
- Process documents in smaller batches
- Use smaller embedding model

**Slow Queries**
- Check `SIMILARITY_THRESHOLD`
- Reduce `top_k`
- Index optimization (ChromaDB auto-handles)

---

**Good luck with your migration! 🚀**
