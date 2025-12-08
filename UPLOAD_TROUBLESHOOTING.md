# 🔧 FastAPI Upload Troubleshooting Guide

## Quick Diagnosis

When you see **"Failed to fetch"**, it means:
1. ❌ FastAPI server is not running, OR
2. ❌ Wrong port (Flask on 5000, FastAPI on 8000), OR  
3. ❌ CORS issue (browser blocking the request), OR
4. ❌ File size too large

---

## ✅ Solution 1: Start FastAPI Server

The FastAPI server must be running on port 8000:

```powershell
# In a NEW terminal (keep Flask running separately):
python run_fastapi.py
```

You should see:
```
🚀 Starting server on 0.0.0.0:8000
📚 API Documentation: http://localhost:8000/docs
✅ Embedding model loaded
✅ Vector store ready: 0 chunks
```

**Keep this terminal open!** Don't close it.

---

## ✅ Solution 2: Test Upload Directly

Use the built-in FastAPI documentation interface:

1. **Open in browser**: http://localhost:8000/docs

2. **Find the `/upload` endpoint** (under "Upload" section)

3. **Click "Try it out"**

4. **Click "Choose File"** and select a document

5. **Click "Execute"**

You should see HTTP 200 response with:
```json
{
  "file_id": "test_document",
  "chunks_ingested": 5,
  "file_format": "txt"
}
```

---

## ✅ Solution 3: Quick PowerShell Test

Run this automated test:

```powershell
.\test_upload.ps1
```

This will:
- ✅ Check if server is running
- ✅ Create/find a test file
- ✅ Upload the file
- ✅ Test semantic search

---

## ✅ Solution 4: Manual cURL Test

```powershell
# Test 1: Check server health
curl.exe http://localhost:8000/health

# Test 2: Upload a file
curl.exe -X POST http://localhost:8000/upload `
    -F "file=@test_document.txt"

# Test 3: Query
$body = '{"query":"test","top_k":3}' 
curl.exe -X POST http://localhost:8000/query `
    -H "Content-Type: application/json" `
    -d $body
```

---

## 🔍 Common Issues

### Issue 1: "Connection refused" or "Failed to fetch"
**Cause:** FastAPI server not running  
**Fix:** Run `python run_fastapi.py` in a separate terminal

### Issue 2: "CORS error" in browser console
**Cause:** Browser security blocking cross-origin requests  
**Fix:** Use the FastAPI docs at http://localhost:8000/docs instead of Flask UI for now

### Issue 3: "File too large"
**Cause:** File exceeds MAX_UPLOAD_SIZE (default 50MB)  
**Fix:** 
```powershell
# In .env file:
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Issue 4: Server starts but immediately exits
**Cause:** Port 8000 already in use  
**Fix:**
```powershell
# Check what's using port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# Kill the process if needed
Stop-Process -Id <ProcessId>
```

---

## 🎯 Quick Resolution Steps

**Right now, do this:**

### Step 1: Open a NEW PowerShell terminal (don't close Flask)

### Step 2: Run FastAPI server
```powershell
cd D:\doc-scanner
python run_fastapi.py
```

### Step 3: In ANOTHER terminal, run the test
```powershell
cd D:\doc-scanner
.\test_upload.ps1
```

### Step 4: Or use browser
Open: http://localhost:8000/docs

---

## 🔄 Running Both Servers Together

You need TWO servers running simultaneously:

**Terminal 1 - Flask (port 5000):**
```powershell
python run.py
```

**Terminal 2 - FastAPI (port 8000):**
```powershell
python run_fastapi.py
```

Then access:
- Flask UI: http://localhost:5000
- FastAPI docs: http://localhost:8000/docs
- FastAPI health: http://localhost:8000/health

---

## 📝 Integration Status

Currently your setup:
- ✅ Flask app exists (your old UI)
- ✅ FastAPI backend created (new vector search)
- ⚠️ **Not yet integrated** (bridge not connected)

To use vector search:
- Use FastAPI docs: http://localhost:8000/docs
- OR run test script: `.\test_upload.ps1`
- OR follow Step 5 in NEXT_STEPS_IMPLEMENTATION.md to connect them

---

## 🚀 Next Actions

1. **Right now**: Start FastAPI server → `python run_fastapi.py`

2. **Test it works**: Run → `.\test_upload.ps1`

3. **Use the features**: Open → http://localhost:8000/docs

4. **Later**: Connect Flask UI to FastAPI (see Step 5 in NEXT_STEPS_IMPLEMENTATION.md)

---

## ❓ Still Not Working?

Check these:

```powershell
# 1. Is Python working?
python --version

# 2. Are dependencies installed?
pip list | Select-String "fastapi|uvicorn|chromadb"

# 3. Is port 8000 free?
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

# 4. Can you reach the server?
Test-NetConnection -ComputerName localhost -Port 8000

# 5. Check server logs
# Look at the terminal where you ran run_fastapi.py
```

If still failing, show me:
1. Output of `python run_fastapi.py`
2. Output of `curl.exe http://localhost:8000/health`
3. Any error messages in browser console (F12)
