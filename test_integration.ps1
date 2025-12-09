# Test Backend Integration
Write-Host ""
Write-Host "🧪 Testing Backend Integration" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Flask is running
Write-Host "1️⃣  Checking Flask server..." -NoNewline
try {
    $flaskHealth = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host " ✅ Running" -ForegroundColor Green
    $flaskRunning = $true
} catch {
    Write-Host " ❌ Not running" -ForegroundColor Red
    Write-Host "   Start Flask: python run.py" -ForegroundColor Yellow
    $flaskRunning = $false
}

# Step 2: Check enhanced routes
if ($flaskRunning) {
    Write-Host ""
    Write-Host "2️⃣  Checking enhanced routes..." -NoNewline
    try {
        $enhancedHealth = Invoke-WebRequest -Uri "http://localhost:5000/api/enhanced/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        $data = $enhancedHealth.Content | ConvertFrom-Json
        Write-Host " ✅ Available" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Status:" -ForegroundColor Cyan
        Write-Host "   • Flask: $($data.flask)" -ForegroundColor White
        Write-Host "   • FastAPI Available: $($data.fastapi_available)" -ForegroundColor White
        if ($data.fastapi_url) {
            Write-Host "   • FastAPI URL: $($data.fastapi_url)" -ForegroundColor White
        }
    } catch {
        Write-Host " ❌ Not available" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Step 3: Check if FastAPI is running
Write-Host ""
Write-Host "3️⃣  Checking FastAPI backend..." -NoNewline
try {
    $fastapiHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host " ✅ Running" -ForegroundColor Green
    $fastapiRunning = $true
} catch {
    Write-Host " ⚠️  Not running" -ForegroundColor Yellow
    Write-Host "   Vector search features disabled" -ForegroundColor Gray
    Write-Host "   Start FastAPI: python run_fastapi.py" -ForegroundColor Yellow
    $fastapiRunning = $false
}

# Step 4: Test enhanced upload if both running
if ($flaskRunning -and $fastapiRunning) {
    Write-Host ""
    Write-Host "4️⃣  Testing enhanced upload..." -NoNewline
    
    # Create test file
    $testFile = ".\test_integration.txt"
    @"
Backend Integration Test Document

This document tests the integration between Flask and FastAPI.
The document should be uploaded through Flask but indexed by FastAPI.

Features tested:
- Document upload via Flask enhanced route
- Vector embedding generation
- Storage in ChromaDB
- Semantic search capability

If you can search for this content, the integration is working!
"@ | Out-File -FilePath $testFile -Encoding UTF8
    
    try {
        # Upload via Flask enhanced route
        $uploadResult = Invoke-RestMethod -Uri "http://localhost:5000/api/enhanced/upload" `
            -Method POST `
            -Form @{ file = Get-Item $testFile } `
            -TimeoutSec 10
        
        if ($uploadResult.status -eq "success") {
            Write-Host " ✅ Success" -ForegroundColor Green
            Write-Host "   Chunks indexed: $($uploadResult.chunks_ingested)" -ForegroundColor Cyan
        } else {
            Write-Host " ⚠️  $($uploadResult.status)" -ForegroundColor Yellow
            Write-Host "   $($uploadResult.message)" -ForegroundColor Gray
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Test search
    Write-Host ""
    Write-Host "5️⃣  Testing semantic search..." -NoNewline
    try {
        $searchBody = @{
            query = "backend integration"
            top_k = 3
        } | ConvertTo-Json
        
        $searchResult = Invoke-RestMethod -Uri "http://localhost:5000/api/enhanced/search" `
            -Method POST `
            -Body $searchBody `
            -ContentType "application/json" `
            -TimeoutSec 10
        
        if ($searchResult.status -eq "success") {
            Write-Host " ✅ Found $($searchResult.total_results) results" -ForegroundColor Green
            if ($searchResult.total_results -gt 0) {
                $topResult = $searchResult.results[0]
                Write-Host "   Top result score: $($topResult.score)" -ForegroundColor Cyan
            }
        } else {
            Write-Host " ❌ Failed" -ForegroundColor Red
        }
    } catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    # Clean up test file
    Remove-Item $testFile -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host ""
if ($flaskRunning) {
    Write-Host "✅ Flask UI: Running (port 5000)" -ForegroundColor Green
    Write-Host "   Your existing UI works as before" -ForegroundColor Gray
} else {
    Write-Host "❌ Flask UI: Not running" -ForegroundColor Red
    Write-Host "   Start with: python run.py" -ForegroundColor Yellow
}
Write-Host ""

if ($fastapiRunning) {
    Write-Host "✅ FastAPI Backend: Running (port 8000)" -ForegroundColor Green
    Write-Host "   Vector search features enabled" -ForegroundColor Gray
} else {
    Write-Host "⚠️  FastAPI Backend: Not running" -ForegroundColor Yellow
    Write-Host "   Flask still works, but no semantic search" -ForegroundColor Gray
    Write-Host "   Start with: python run_fastapi.py" -ForegroundColor Yellow
}
Write-Host ""

if ($flaskRunning -and $fastapiRunning) {
    Write-Host "🎉 Full Integration Active!" -ForegroundColor Green
    Write-Host ""
    Write-Host "New enhanced endpoints available:" -ForegroundColor Cyan
    Write-Host "  POST /api/enhanced/upload   - Upload with vector indexing" -ForegroundColor White
    Write-Host "  POST /api/enhanced/search   - Semantic search" -ForegroundColor White
    Write-Host "  POST /api/enhanced/rag      - Get RAG context" -ForegroundColor White
    Write-Host "  POST /api/enhanced/analyze  - Enhanced analysis" -ForegroundColor White
    Write-Host "  GET  /api/enhanced/stats    - System statistics" -ForegroundColor White
    Write-Host "  GET  /api/enhanced/health   - Backend status" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 See BACKEND_INTEGRATION.md for details" -ForegroundColor Cyan
}

Write-Host ""
