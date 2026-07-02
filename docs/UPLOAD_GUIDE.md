# 📤 Document Upload Guide

## Where to Upload Documents

Your FastAPI server has an **interactive web interface** for uploading and testing.

### 🌐 Access the Upload Interface

**Open in your browser:** http://localhost:8000/docs

---

## 📋 Step-by-Step Upload Instructions

### Step 1: Open the API Documentation
```
http://localhost:8000/docs
```

### Step 2: Find the Upload Section
- Scroll down to the **green "Upload"** section
- You'll see: **`POST /upload`** - Upload document for ingestion

### Step 3: Try It Out
1. Click the **"Try it out"** button (top right of that section)
2. You'll see a **"Choose File"** button appear

### Step 4: Select Your File
1. Click **"Choose File"**
2. Navigate to your document
3. Select any of these formats:
   - ✅ PDF (`.pdf`)
   - ✅ Word (`.docx`)
   - ✅ Text (`.txt`)
   - ✅ Markdown (`.md`)
   - ✅ HTML (`.html`)
   - ✅ AsciiDoc (`.adoc`)
   - ✅ ZIP (with documents inside)

### Step 5: Execute Upload
1. Click the blue **"Execute"** button
2. Wait a few seconds (you'll see a spinner)

### Step 6: See Results
You'll get a response like:
```json
{
  "status": "success",
  "file_id": "my_document_abc123",
  "chunks_ingested": 15,
  "file_format": "pdf",
  "message": "Document uploaded and ingested successfully"
}
```

---

## 🔍 After Upload: Test Search

### Step 1: Find Query Section
- Scroll to the **blue "Query"** section
- Find: **`POST /query`** - Semantic search

### Step 2: Try It Out
1. Click **"Try it out"**
2. You'll see a JSON editor

### Step 3: Enter Your Query
Replace the default JSON with:
```json
{
  "query": "your search term here",
  "top_k": 5
}
```

Example:
```json
{
  "query": "security best practices",
  "top_k": 5
}
```

### Step 4: Execute Search
1. Click **"Execute"**
2. See your semantic search results!

---

## 🖼️ What You Should See

### Main Page (http://localhost:8000/docs)

```
╔══════════════════════════════════════════╗
║  FastAPI Documentation                   ║
║  Doc Scanner RAG API                     ║
╚══════════════════════════════════════════╝

📗 Health
  GET  /health              - Basic health check
  GET  /health/stats        - Detailed statistics
  GET  /health/ready        - Readiness probe

📗 Upload                    ← YOU ARE HERE!
  POST /upload              - Upload document
  GET  /upload/list         - List all uploads
  DELETE /upload/{file_id}  - Delete document

📗 Query
  POST /query               - Semantic search
  POST /query/rag           - RAG context
  GET  /query/similar       - Find similar

📗 Analyze
  POST /analyze             - Analyze text
  GET  /analyze/rules       - List rules
```

### Upload Section Detail

```
POST /upload  Upload document for ingestion

[Try it out]  ← CLICK THIS FIRST

Parameters:
file *  [Choose File]  ← THEN CLICK THIS
        No file chosen

[Execute]  ← FINALLY CLICK THIS
```

---

## 🚀 Quick Test (PowerShell)

Don't want to use the browser? Use this command:

```powershell
# Upload a document
curl.exe -X POST http://localhost:8000/upload -F "file=@C:\path\to\your\document.pdf"

# Search for content
$body = '{"query":"your search","top_k":5}'
curl.exe -X POST http://localhost:8000/query -H "Content-Type: application/json" -d $body
```

Or use the test script:
```powershell
.\test_upload.ps1
```

---

## 📂 Where Are Files Stored?

After upload:
- **Original files**: `./uploads/` directory
- **Vector embeddings**: `./chroma_db/` directory
- **Metadata**: In ChromaDB

---

## ❓ Troubleshooting

### "I don't see the Choose File button"
- Make sure you clicked **"Try it out"** first
- Refresh the page

### "Upload failed"
- Check file size (max 50MB by default)
- Ensure file format is supported
- Check server logs in terminal

### "Server not responding"
- Check if FastAPI is running: `http://localhost:8000/health`
- Start it if needed: `python run_fastapi.py`

### "Can't find the page"
- Ensure you're on port **8000** (not 5000)
- Flask is on 5000, FastAPI is on 8000

---

## 🎯 Quick Access Links

- **Upload Interface**: http://localhost:8000/docs#/Upload/upload_document_upload_post
- **Full API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Statistics**: http://localhost:8000/health/stats

---

## 📊 What Happens When You Upload?

1. **File Upload** → Server receives your document
2. **Parsing** → Extracts text from PDF/DOCX/etc.
3. **Chunking** → Splits text into ~300-word chunks
4. **Embedding** → Converts each chunk to 384-dim vector
5. **Storage** → Saves to ChromaDB vector database
6. **Ready** → Document is now searchable!

---

## 🎉 Next Steps After Upload

1. **Test Search**: Use the `/query` endpoint
2. **Try RAG**: Use `/query/rag` for LLM-ready context
3. **Analyze**: Use `/analyze` for rule-based checking
4. **Upload More**: Add multiple documents to build your knowledge base

---

## 💡 Pro Tips

- **Upload multiple files**: They all go into the same vector store
- **Search across all**: Queries search ALL uploaded documents
- **Check stats**: Use `/health/stats` to see total chunks
- **List files**: Use `/upload/list` to see what's uploaded
- **Delete files**: Use DELETE `/upload/{file_id}` to remove

---

Need help? The interactive docs at http://localhost:8000/docs have **"Try it out"** buttons for everything!
