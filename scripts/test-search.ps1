# Test Semantic Search - Quick CLI Tester
# This script tests the semantic search functionality via command line

Write-Host "🔍 Semantic Search Tester" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if Flask is running
$flaskRunning = Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet
if (-not $flaskRunning) {
    Write-Host "❌ Flask server not running on port 5000" -ForegroundColor Red
    Write-Host "Start Flask first: python run.py" -ForegroundColor Yellow
    exit 1
}

# Check if FastAPI is running
$fastAPIRunning = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet
if (-not $fastAPIRunning) {
    Write-Host "❌ FastAPI server not running on port 8000" -ForegroundColor Red
    Write-Host "Start FastAPI first: cd fastapi_backend; python -m uvicorn main:app --host 0.0.0.0 --port 8000" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Both servers running" -ForegroundColor Green
Write-Host ""

# Check vector store status
Write-Host "📊 Checking vector store status..." -ForegroundColor Cyan
try {
    $statsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/stats" -Method Get
    Write-Host "   📚 Total documents: $($statsResponse.total_documents)" -ForegroundColor White
    Write-Host "   📄 Total chunks: $($statsResponse.total_chunks)" -ForegroundColor White
    Write-Host "   🧠 Embedding model: $($statsResponse.embedding_model)" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Could not get stats: $_" -ForegroundColor Red
    exit 1
}

# Check if there are documents to search
if ($statsResponse.total_chunks -eq 0) {
    Write-Host "⚠️  No documents in vector store" -ForegroundColor Yellow
    Write-Host "Upload some documents first using:" -ForegroundColor Yellow
    Write-Host "   .\upload.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or test with FastAPI directly - see UPLOAD_GUIDE.md" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

# Get search query from user
Write-Host "🔍 Enter search query:" -ForegroundColor Cyan
Write-Host "   Examples:" -ForegroundColor Gray
Write-Host "   - security best practices" -ForegroundColor Gray
Write-Host "   - error handling" -ForegroundColor Gray
Write-Host "   - configuration options" -ForegroundColor Gray
Write-Host ""
$query = Read-Host "Query"

if ([string]::IsNullOrWhiteSpace($query)) {
    Write-Host "❌ Query cannot be empty" -ForegroundColor Red
    exit 1
}

# Perform search via Flask API
Write-Host ""
Write-Host "🔍 Searching for: '$query'" -ForegroundColor Cyan
Write-Host "Loading..." -ForegroundColor Gray

$searchBody = @{
    query = $query
    top_k = 5
} | ConvertTo-Json

try {
    $searchResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/enhanced/search" `
                                        -Method Post `
                                        -ContentType "application/json" `
                                        -Body $searchBody
    
    Write-Host ""
    Write-Host "=" * 50
    Write-Host "✅ Search completed!" -ForegroundColor Green
    Write-Host "   Found: $($searchResponse.total_results) results" -ForegroundColor White
    Write-Host "   Time: $([math]::Round($searchResponse.search_time * 1000, 2))ms" -ForegroundColor White
    Write-Host "=" * 50
    Write-Host ""
    
    if ($searchResponse.results.Count -eq 0) {
        Write-Host "📭 No results found" -ForegroundColor Yellow
        Write-Host "   Try a different query or upload more documents" -ForegroundColor Gray
    } else {
        # Display results
        for ($i = 0; $i -lt $searchResponse.results.Count; $i++) {
            $result = $searchResponse.results[$i]
            $similarity = [math]::Round($result.similarity * 100, 1)
            
            # Color based on similarity
            $scoreColor = if ($similarity -gt 70) { "Green" } 
                         elseif ($similarity -gt 50) { "Yellow" } 
                         else { "Gray" }
            
            Write-Host "┌──────────────────────────────────────────────────┐" -ForegroundColor DarkGray
            Write-Host "│ " -NoNewline -ForegroundColor DarkGray
            Write-Host "Result $($i + 1)" -NoNewline -ForegroundColor White
            if ($result.metadata.filename) {
                Write-Host " - $($result.metadata.filename)" -NoNewline -ForegroundColor DarkCyan
            }
            Write-Host " [" -NoNewline -ForegroundColor DarkGray
            Write-Host "$similarity%" -NoNewline -ForegroundColor $scoreColor
            Write-Host " match]" -ForegroundColor DarkGray
            Write-Host "├──────────────────────────────────────────────────┤" -ForegroundColor DarkGray
            
            # Text (wrap at 50 chars)
            $text = $result.text
            if ($text.Length -gt 200) {
                $text = $text.Substring(0, 200) + "..."
            }
            $wrapped = ($text -split "(.{1,48})" | Where-Object { $_ }) -join "`n│ "
            Write-Host "│ " -NoNewline -ForegroundColor DarkGray
            Write-Host $wrapped -ForegroundColor White
            
            # Metadata
            if ($result.metadata.chunk_index -ne $null) {
                Write-Host "│" -ForegroundColor DarkGray
                Write-Host "│ " -NoNewline -ForegroundColor DarkGray
                Write-Host "ℹ️  Chunk $($result.metadata.chunk_index + 1)" -NoNewline -ForegroundColor DarkGray
                if ($result.metadata.total_chunks) {
                    Write-Host " of $($result.metadata.total_chunks)" -ForegroundColor DarkGray
                } else {
                    Write-Host "" -ForegroundColor DarkGray
                }
            }
            
            Write-Host "└──────────────────────────────────────────────────┘" -ForegroundColor DarkGray
            Write-Host ""
        }
    }
    
    # Offer to search again
    Write-Host ""
    $again = Read-Host "Search again? (y/n)"
    if ($again -eq "y") {
        & $MyInvocation.MyCommand.Path
    } else {
        Write-Host ""
        Write-Host "💡 You can also test in the web UI:" -ForegroundColor Cyan
        Write-Host "   http://localhost:5000" -ForegroundColor White
        Write-Host "   Look for the 'Semantic Search' card in the left sidebar" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Search failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check Flask logs for errors" -ForegroundColor Gray
    Write-Host "2. Verify FastAPI is responding: curl http://localhost:8000/health" -ForegroundColor Gray
    Write-Host "3. See UPLOAD_GUIDE.md for troubleshooting steps" -ForegroundColor Gray
}
